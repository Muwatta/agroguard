from flask import Flask, render_template, jsonify, Response
import time
import traceback
import os
import json
from collections import Counter
from datetime import datetime

print("Starting imports...")

# Import camera module
from camera import Camera, gen_frames

# Import other modules
from vision import detect_motion, save_capture
print("Vision imported")

from classifier import classify
print("Classifier imported")

from tracker import register_visit
print("Tracker imported")

from advisory import get_advice
print("Advisory imported")

from storage import log_event, get_events
print("Storage imported")

app = Flask(__name__)
print("Flask app created")

camera = Camera(0)  
camera.start()

# Template filter for datetime
@app.template_filter('datetime')
def format_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

# Context processor
@app.context_processor
def inject_config():
    from config import CAMERA_URL, CONF_THRESHOLD, VISIT_WINDOW_SEC
    return dict(config={
        'CAMERA_URL': CAMERA_URL,
        'CONF_THRESHOLD': CONF_THRESHOLD,
        'VISIT_WINDOW_SEC': VISIT_WINDOW_SEC
    })

# NOW DEFINE ROUTES (after app is created)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(gen_frames(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/snapshot')
def snapshot():
    """Get single snapshot"""
    frame = camera.get_frame()
    if frame:
        return Response(frame, mimetype='image/jpeg')
    return 'No frame available', 404

@app.route("/")
def index():
    events = get_events()
    
    total_events = len(events)
    unique_pests = len(set(e[1] for e in events))
    
    pest_counts = Counter(e[1] for e in events)
    pest_labels = list(pest_counts.keys())
    pest_counts_values = list(pest_counts.values())
    
    last_alert_time = format_datetime(events[0][0]) if events else "No alerts"
    
    today = datetime.now().date()
    captures_today = len([e for e in events if datetime.fromtimestamp(e[0]).date() == today])
    total_alerts = len([e for e in events if e[2] > 0.6])
    
    return render_template("index.html", 
                         events=events,
                         total_events=total_events,
                         unique_pests=unique_pests,
                         pest_labels=pest_labels,
                         pest_counts=pest_counts_values,
                         last_alert_time=last_alert_time,
                         captures_today=captures_today,
                         total_alerts=total_alerts)

@app.route("/live")
def live_feed():
    return render_template("live.html")

@app.route("/analytics")
def analytics():
    events = get_events()
    
    hours = [datetime.fromtimestamp(e[0]).hour for e in events]
    hourly_counts = Counter(hours)
    
    confidences = [e[2] for e in events] if events else []
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    return render_template("analytics.html",
                         events=events,
                         hourly_counts=hourly_counts,
                         avg_confidence=avg_confidence)

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/api/events")
def api_events():
    return jsonify(get_events())

@app.route("/api/stats")
def api_stats():
    events = get_events()
    return jsonify({
        "total": len(events),
        "unique_pests": len(set(e[1] for e in events)),
        "last_alert": events[0][0] if events else None
    })

@app.route("/api/settings", methods=["POST"])
def save_settings():
    try:
        data = request.get_json()
        with open("settings.json", "w") as f:
            json.dump(data, f, indent=2)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Background detection loop
def agroguard_loop():
    try:
        frame, motion = detect_motion()
        if not motion:
            return

        img_path, ts = save_capture(frame)
        print(f"Captured: {img_path}")

        pest, conf = classify(img_path)
        print(f"Classified: {pest} ({conf:.2f})")

        if conf < 0.6:
            return

        persistent = register_visit(pest)
        if not persistent:
            return

        advice = get_advice(pest)
        log_event(ts, pest, conf, img_path, advice)

        print("ALERT:", pest, conf)
    except Exception as e:
        print(f"Error in agroguard_loop: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    import threading

    def loop():
        print("Starting detection loop...")
        while True:
            agroguard_loop()
            time.sleep(1)

    threading.Thread(target=loop, daemon=True).start()
    print("Starting Flask server on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)