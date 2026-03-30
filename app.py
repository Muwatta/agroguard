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
from classifier import classify
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
    try:
        frame, motion = detect_motion(camera)
        if not motion:
            return

        img_path, ts = save_capture(frame)
        print(f"Captured: {os.path.basename(img_path)}")

        pest, conf = classify(img_path)
        print(f"Classified: {pest} ({conf:.2f})")

        if conf < 0.6:
            return

        persistent = register_visit(pest)
        if not persistent:
            return

        advice = get_advice(pest)
        log_event(ts, pest, conf, img_path, advice)
        
        hardware.alert_buzzer(1)
        
        if pest in ["armyworm", "beetle", "weevil"] and conf > 0.8:
            print(f"Critical pest detected - activating defenses!")
            hardware.sprinkler_on(10)
            if arduino.connected:
                arduino.sprinkler_on(10)
        
        print(f"ALERT: {pest} {conf:.2f}")
        
    except Exception as e:
        print(f"Error in detection loop: {e}")
        traceback.print_exc()

@app.route("/")
def index():
    events = get_events()
    total = len(events)
    unique = len(set(e[1] for e in events))
    pest_counts = Counter(e[1] for e in events)
    today = datetime.now().date()
    captures_today = len([e for e in events if datetime.fromtimestamp(e[0]).date() == today])
    
    return render_template("index.html",
                         events=events[:10],
                         total_events=total,
                         unique_pests=unique,
                         pest_labels=list(pest_counts.keys()),
                         pest_counts=list(pest_counts.values()),
                         last_alert_time=format_datetime(events[0][0]) if events else "None",
                         captures_today=captures_today,
                         total_alerts=total)

@app.route("/live")
def live_feed():
    return render_template("live.html")

@app.route("/analytics")
def analytics():
    events = get_events()
    hours = [datetime.fromtimestamp(e[0]).hour for e in events]
    hourly_counts = Counter(hours)
    confs = [e[2] for e in events if events]
    avg_conf = sum(confs)/len(confs) if confs else 0
    
    return render_template("analytics.html",
                         events=events,
                         hourly_counts=hourly_counts,
                         avg_confidence=avg_conf)

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/hardware")
def hardware_status():
    return render_template("hardware.html",
                         status=hardware.get_status(),
                         arduino_connected=arduino.connected)

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/api/events")
def api_events():
    return jsonify(get_events())

@app.route("/api/stats")
def api_stats():
    events = get_events()
    return jsonify({
        "total": len(events),
        "unique_pests": len(set(e[1] for e in events)),
        "last_alert": events[0][0] if events else None,
        "hardware": hardware.get_status(),
        "arduino": arduino.get_sensor_data() if arduino.connected else None
    })

@app.route("/api/sprinkler", methods=["POST"])
def api_sprinkler():
    data = request.get_json() or {}
    duration = data.get('duration', 10)
    hardware.sprinkler_on(duration)
    return jsonify({"status": "success", "duration": duration})

@app.route("/api/buzzer", methods=["POST"])
def api_buzzer():
    hardware.alert_buzzer(2)
    return jsonify({"status": "success"})

@app.route("/api/sensors")
def api_sensors():
    return jsonify({
        "hardware": hardware.get_status(),
        "arduino": arduino.get_sensor_data() if arduino.connected else None
    })


@app.route("/api/retrain", methods=["POST"])
def api_retrain():
    import subprocess
    try:
        result = subprocess.run(["python", "retrain_with_none.py"], capture_output=True, text=True, check=True)
        return jsonify({"status": "success", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "error": e.stderr}), 500

if __name__ == "__main__":
    def detection_thread():
        print("Detection loop started")
        while True:
            agroguard_loop()
            time.sleep(1)
    
    threading.Thread(target=detection_thread, daemon=True).start()
    print("Server starting on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
