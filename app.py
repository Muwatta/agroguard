import cv2
import time
import traceback
import os
import json
import threading
from collections import Counter
from datetime import datetime, timedelta
import platform

from flask import Flask, render_template, jsonify, Response, request

from camera import Camera, gen_frames
from vision import detect_motion, save_capture
from classifier import classify, get_classifier
from tracker import register_visit
from advisory import get_advice
from storage import log_event, get_events
from hardware_controller import hardware
from arduino_controller import arduino

print(f"Starting AgroGuard AI on {platform.system()}")

app = Flask(__name__)

camera = Camera(0)
camera.start()

# Global variables for sprinkler cooldown
last_sprinkler_time = None
SPRINKLER_COOLDOWN = 30  # seconds between sprinkler activations

# Face cascade (load once)
face_cascade = None

def get_face_cascade():
    """Load face cascade classifier"""
    global face_cascade
    if face_cascade is None:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        if face_cascade.empty():
            print("Warning: Could not load face cascade")
        else:
            print("Face cascade loaded")
    return face_cascade

def contains_face(frame):
    """Detect if frame contains a human face"""
    try:
        cascade = get_face_cascade()
        if cascade.empty():
            return False
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
        
        if len(faces) > 0:
            print(f"Face detected - skipping frame")
            return True
        return False
    except Exception as e:
        print(f"Face detection error: {e}")
        return False

def agroguard_loop():
    global last_sprinkler_time
    
    try:
        frame, motion = detect_motion(camera)
        
        if frame is None:
            return
            
        if not motion:
            return
            
        # Skip if face detected
        if contains_face(frame):
            return

        img_path, ts = save_capture(frame)
        print(f"Captured: {os.path.basename(img_path)}")

        pest, conf = classify(img_path)
        print(f"Classified: {pest} ({conf:.2f})")

        from config import CONF_THRESHOLD

        # Skip none class (background/face)
        if pest == 'none':
            print(f"Classified as 'none' (background) - skipping")
            return
            
        # Skip unidentified or low confidence
        if pest == 'unidentified' or conf < CONF_THRESHOLD:
            print(f"Skipping: pest={pest}, confidence={conf:.2f}")
            return

        persistent = register_visit(pest)
        if not persistent:
            print(f"Pest {pest} not persistent enough, skipping")
            return

        advice = get_advice(pest)
        log_event(ts, pest, conf, img_path, advice)
        
        hardware.alert_buzzer(1)
        
        critical_pests = ["armyworm", "aphid", "mealybugs", "stem_borers", "weevil"]
        if pest in critical_pests and conf > 0.8:
            print(f"Critical pest detected - activating defenses!")
            
            current_time = datetime.now()
            if last_sprinkler_time is None or (current_time - last_sprinkler_time).seconds > SPRINKLER_COOLDOWN:
                hardware.sprinkler_on(10)
                if arduino.connected:
                    arduino.sprinkler_on(10)
                last_sprinkler_time = current_time
                print(f"Sprinkler activated (cooldown: {SPRINKLER_COOLDOWN}s)")
            else:
                seconds_remaining = SPRINKLER_COOLDOWN - (current_time - last_sprinkler_time).seconds
                print(f"Sprinkler in cooldown ({seconds_remaining}s remaining)")
        
        print(f"ALERT: {pest} detected with {conf:.2f} confidence")
        
        # After pest is confirmed and logged
        if pest != 'none' and conf > CONF_THRESHOLD:
            # Send to Arduino OLED
            arduino.send_pest_alert(pest, conf)
    except Exception as e:
        print(f"Error in detection loop: {e}")
        traceback.print_exc()

# Template Filters
@app.template_filter('datetime')
def format_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

@app.context_processor
def inject_globals():
    from config import CAMERA_URL, CONF_THRESHOLD
    return {
        'config': {'CAMERA_URL': CAMERA_URL, 'CONF_THRESHOLD': CONF_THRESHOLD},
        'platform': platform.system(),
        'hardware_mode': hardware.simulation_mode
    }

# Web Routes
@app.route('/')
def index():
    try:
        events = get_events()
        total = len(events)
        
        # Initialize default values
        unique = 0
        pest_counts = {}
        captures_today = 0
        active_alerts = 0
        critical_pests = {"armyworm", "aphid", "mealybugs", "stem_borers", "weevil"}
        
        if events and len(events) > 0:
            if isinstance(events[0], dict):
                # New format (dict)
                unique = len(set(e['pest'] for e in events))
                pest_counts = Counter(e['pest'] for e in events)
                captures_today = len([e for e in events if datetime.fromtimestamp(e['timestamp']).date() == datetime.now().date()])
                active_alerts = len([e for e in events if e['pest'] in critical_pests and e['confidence'] >= 0.80])
            else:
                # Old format (tuple)
                unique = len(set(e[1] for e in events))
                pest_counts = Counter(e[1] for e in events)
                captures_today = len([e for e in events if datetime.fromtimestamp(e[0]).date() == datetime.now().date()])
                active_alerts = len([e for e in events if e[1] in critical_pests and e[2] >= 0.80])
        
        classifier = get_classifier()
        if classifier.interpreter is None:
            model_status = "Fallback"
        else:
            expected_cls = len(classifier.class_names) if classifier.class_names else 0
            model_status = f"Active ({expected_cls} classes)"

        camera_status = "Online" if camera.camera and camera.camera.isOpened() else "Offline"
        
        last_alert = "None"
        if events:
            if isinstance(events[0], dict):
                last_alert = format_datetime(events[0]['timestamp'])
            else:
                last_alert = format_datetime(events[0][0])

        return render_template("index.html",
                             events=events[:10],
                             total_events=total,
                             unique_pests=unique,
                             pest_labels=list(pest_counts.keys()),
                             pest_counts=list(pest_counts.values()),
                             last_alert_time=last_alert,
                             captures_today=captures_today,
                             total_alerts=active_alerts,
                             ai_model_status=model_status,
                             camera_status=camera_status)
    except Exception as e:
        print(f"Error in index route: {e}")
        traceback.print_exc()
        return render_template("index.html", error=str(e)), 500

@app.route('/live')
def live_feed():
    return render_template("live.html")

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    try:
        events = get_events()
        hourly_counts = {}
        avg_conf = 0
        
        if events and len(events) > 0:
            # Handle both dict and tuple formats
            if isinstance(events[0], dict):
                hours = [datetime.fromtimestamp(e['timestamp']).hour for e in events]
                confs = [e['confidence'] for e in events]
            else:
                hours = [datetime.fromtimestamp(e[0]).hour for e in events]
                confs = [e[2] for e in events if events]
            hourly_counts = Counter(hours)
            avg_conf = sum(confs)/len(confs) if confs else 0
        
        return render_template("analytics.html",
                             events=events,
                             hourly_counts=hourly_counts,
                             avg_confidence=avg_conf)
    except Exception as e:
        print(f"Error in analytics route: {e}")
        traceback.print_exc()
        return render_template("analytics.html", error=str(e)), 500
    
@app.route('/settings')
def settings():
    return render_template("settings.html")

@app.route('/hardware')
def hardware_status():
    return render_template("hardware.html",
                         status=hardware.get_status(),
                         arduino_connected=arduino.connected)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# API Routes
@app.route('/api/events')
def api_events():
    try:
        return jsonify(get_events())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def api_stats():
    try:
        events = get_events()
        unique_pests = 0
        if events and len(events) > 0:
            if isinstance(events[0], dict):
                unique_pests = len(set(e['pest'] for e in events))
            else:
                unique_pests = len(set(e[1] for e in events))
        
        last_alert = None
        if events:
            if isinstance(events[0], dict):
                last_alert = events[0]['timestamp']
            else:
                last_alert = events[0][0]
        
        return jsonify({
            "total": len(events),
            "unique_pests": unique_pests,
            "last_alert": last_alert,
            "hardware": hardware.get_status(),
            "arduino": arduino.get_sensor_data() if arduino.connected else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sprinkler', methods=['POST'])
def api_sprinkler():
    try:
        data = request.get_json() or {}
        duration = data.get('duration', 10)
        hardware.sprinkler_on(duration)
        return jsonify({"status": "success", "duration": duration})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/buzzer', methods=['POST'])
def api_buzzer():
    try:
        hardware.alert_buzzer(2)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sensors')
def api_sensors():
    try:
        return jsonify({
            "hardware": hardware.get_status(),
            "arduino": arduino.get_sensor_data() if arduino.connected else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main Entry Point
if __name__ == "__main__":
    def detection_thread():
        print("Detection loop started")
        while True:
            try:
                agroguard_loop()
                time.sleep(1)
            except Exception as e:
                print(f"Error in detection thread: {e}")
                traceback.print_exc()
                time.sleep(2)
    
    threading.Thread(target=detection_thread, daemon=True).start()
    print("Server starting on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)