from flask import Flask, render_template, jsonify
import time

from vision import detect_motion, save_capture
from classifier import classify
from tracker import register_visit
from advisory import get_advice
from storage import log_event, get_events

app = Flask(__name__)

def agroguard_loop():
    frame, motion = detect_motion()
    if not motion:
        return

    img_path, ts = save_capture(frame)

    pest, conf = classify(img_path)

    if conf < 0.6:
        return

    persistent = register_visit(pest)
    if not persistent:
        return

    advice = get_advice(pest)

    log_event(ts, pest, conf, img_path, advice)

    print("ALERT:", pest, conf)


@app.route("/")
def index():
    events = get_events()
    return render_template("index.html", events=events)


@app.route("/api/events")
def api_events():
    return jsonify(get_events())


if __name__ == "__main__":
    import threading

    def loop():
        while True:
            agroguard_loop()
            time.sleep(1)

    threading.Thread(target=loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
