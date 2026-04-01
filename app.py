from flask import Flask, render_template, jsonify, Response, request
import time
import traceback
import os
import json
from collections import Counter
from datetime import datetime
import platform
import threading

print(f"Starting AgroGuard AI on {platform.system()}")

from camera import Camera, gen_frames
from vision import detect_motion, save_capture
from classifier import classify, get_classifier
from tracker import register_visit
from advisory import get_advice
from storage import log_event, get_events
from hardware_controller import hardware
from arduino_controller import arduino

print("All modules imported")

app = Flask(__name__)

camera = Camera(0)
camera.start()

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

def agroguard_loop():
    """Main detection loop with improved error handling"""
    try:
        # Call detect_motion with camera object
        frame, motion = detect_motion(camera)
        
        if frame is None:
            print("Warning: No frame received from camera")
            return
            
        if not motion:
            return

        # Save captured frame
        img_path, ts = save_capture(frame)
        print(f"Captured: {os.path.basename(img_path)}")

        # Classify the pest
        pest, conf = classify(img_path)
        print(f"Classified: {pest} ({conf:.2f})")

        from config import CONF_THRESHOLD

        # Skip unidentified or low confidence detections
        if pest == 'unidentified' or conf < CONF_THRESHOLD:
            print(f"Skipping: pest={pest}, confidence={conf:.2f}")
            return

        # Require persistence to reduce transient false positives
        persistent = register_visit(pest)
        if not persistent:
            print(f"Pest {pest} not persistent enough, skipping")
            return

        # Get advice and log event
        advice = get_advice(pest)
        log_event(ts, pest, conf, img_path, advice)
        
        # Trigger hardware alerts
        hardware.alert_buzzer(1)
        
        # Critical pest response
        critical_pests = ["armyworm", "aphid", "mealybug", "stem_borer", "weevil"]
        if pest in critical_pests and conf > 0.8:
            print(f"Critical pest detected - activating defenses!")
            hardware.sprinkler_on(10)
            if arduino.connected:
                arduino.sprinkler_on(10)
        
        print(f"ALERT: {pest} detected with {conf:.2f} confidence")
        
    except Exception as e:
        print(f"Error in detection loop: {e}")
        traceback.print_exc()

@app.route("/")
def index():
    """Home page with dashboard"""
    try:
        events = get_events()
        total = len(events)
        unique = len(set(e[1] for e in events))
        pest_counts = Counter(e[1] for e in events)
        today = datetime.now().date()
        captures_today = len([e for e in events if datetime.fromtimestamp(e[0]).date() == today])

        # Critical pests
        critical_pests = {"armyworm", "aphid", "mealybug", "stem_borer", "weevil"}
        active_alerts = len([e for e in events if e[1] in critical_pests and e[2] >= 0.80])
        
        # AI model status from classifier
        classifier = get_classifier()
        if classifier.interpreter is None:
            model_status = "Fallback"
        else:
            expected_cls = len(classifier.class_names) if classifier.class_names else 0
            output_dim = classifier.model_output_dim if hasattr(classifier, 'model_output_dim') else None
            if output_dim is not None and expected_cls != output_dim:
                model_status = f"Active (mismatch: output {output_dim} vs classes {expected_cls})"
            else:
                model_status = f"Active ({expected_cls} classes)"

        # Camera status
        camera_status = "Online" if camera.camera and camera.camera.isOpened() else "Offline"

        return render_template("index.html",
                             events=events[:10],
                             total_events=total,
                             unique_pests=unique,
                             pest_labels=list(pest_counts.keys()),
                             pest_counts=list(pest_counts.values()),
                             last_alert_time=format_datetime(events[0][0]) if events else "None",
                             captures_today=captures_today,
                             total_alerts=active_alerts,
                             ai_model_status=model_status,
                             camera_status=camera_status)
    except Exception as e:
        print(f"Error in index route: {e}")
        traceback.print_exc()
        return render_template("error.html", error=str(e)), 500

@app.route("/live")
def live_feed():
    """Live camera feed page"""
    return render_template("live.html")

@app.route("/analytics")
def analytics():
    """Analytics dashboard"""
    try:
        events = get_events()
        hours = [datetime.fromtimestamp(e[0]).hour for e in events]
        hourly_counts = Counter(hours)
        confs = [e[2] for e in events if events]
        avg_conf = sum(confs)/len(confs) if confs else 0
        
        return render_template("analytics.html",
                             events=events,
                             hourly_counts=hourly_counts,
                             avg_confidence=avg_conf)
    except Exception as e:
        print(f"Error in analytics route: {e}")
        traceback.print_exc()
        return render_template("error.html", error=str(e)), 500

@app.route("/settings")
def settings():
    """Settings page"""
    return render_template("settings.html")

@app.route("/hardware")
def hardware_status():
    """Hardware control page"""
    return render_template("hardware.html",
                         status=hardware.get_status(),
                         arduino_connected=arduino.connected)

@app.route("/video_feed")
def video_feed():
    """Video streaming route"""
    return Response(gen_frames(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/api/events")
def api_events():
    """API endpoint for events"""
    try:
        return jsonify(get_events())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats")
def api_stats():
    """API endpoint for statistics"""
    try:
        events = get_events()
        return jsonify({
            "total": len(events),
            "unique_pests": len(set(e[1] for e in events)),
            "last_alert": events[0][0] if events else None,
            "hardware": hardware.get_status(),
            "arduino": arduino.get_sensor_data() if arduino.connected else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sprinkler", methods=["POST"])
def api_sprinkler():
    """API endpoint to control sprinkler"""
    try:
        data = request.get_json() or {}
        duration = data.get('duration', 10)
        hardware.sprinkler_on(duration)
        return jsonify({"status": "success", "duration": duration})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/buzzer", methods=["POST"])
def api_buzzer():
    """API endpoint to control buzzer"""
    try:
        hardware.alert_buzzer(2)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sensors")
def api_sensors():
    """API endpoint for sensor data"""
    try:
        return jsonify({
            "hardware": hardware.get_status(),
            "arduino": arduino.get_sensor_data() if arduino.connected else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/retrain", methods=["POST"])
def api_retrain():
    """API endpoint to retrain the model"""
    import subprocess
    try:
        result = subprocess.run(["python", "retrain_with_none.py"], 
                              capture_output=True, text=True, check=True)
        return jsonify({"status": "success", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "error": e.stderr}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    def detection_thread():
        """Background thread for continuous detection"""
        print("Detection loop started")
        while True:
            try:
                agroguard_loop()
                time.sleep(1)  # Wait 1 second between detections
            except Exception as e:
                print(f"Error in detection thread: {e}")
                traceback.print_exc()
                time.sleep(2)  # Wait longer on error
    
    # Start detection thread
    threading.Thread(target=detection_thread, daemon=True).start()
    print("Server starting on http://0.0.0.0:5000")
    
    # Run Flask app
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)