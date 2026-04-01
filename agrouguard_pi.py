#!/usr/bin/env python3
"""
AgroGuard – Raspberry Pi 4 Controller
- Reads soil moisture from Arduino over serial
- Runs pest detection (TFLite) on camera frames
- Triggers pest deterrent on detection
- Serves live dashboard on http://<pi-ip>:5000

Camera source (set in .env):
    PHONE_CAM_URL=http://<laptop-ip>:8080/video   <- laptop stream
    PHONE_CAM_URL=0                                <- USB/Pi camera

Install on Pi:
    pip3 install flask opencv-python-headless tflite-runtime pyserial python-dotenv
"""

import os, time, threading, logging
from datetime import datetime
from collections import deque
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

import cv2
import numpy as np
from flask import Flask, Response, jsonify, render_template_string

# GPIO
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    DETERRENT_PIN = int(os.environ.get("DETERRENT_PIN", "17"))
    GPIO.setup(DETERRENT_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO_OK = True
except (ImportError, RuntimeError):
    GPIO_OK = False

# Serial
try:
    import serial
    SERIAL_OK = True
except ImportError:
    SERIAL_OK = False

# TFLite
try:
    from tflite_runtime.interpreter import Interpreter
    TFLITE_OK = True
except ImportError:
    try:
        import tensorflow.lite as tflite
        Interpreter = tflite.Interpreter
        TFLITE_OK = True
    except ImportError:
        TFLITE_OK = False

# Config
SERIAL_PORT    = os.environ.get("SERIAL_PORT",      "/dev/ttyUSB0")
BAUD_RATE      = int(os.environ.get("BAUD_RATE",    "9600"))
MODEL_PATH     = os.environ.get("MODEL_PATH",       "pest_model.tflite")
CONF_THRESHOLD = float(os.environ.get("CONF_THRESHOLD", "0.65"))
DETERRENT_SECS = int(os.environ.get("DETERRENT_SECS",   "3"))
IMG_SIZE       = int(os.environ.get("IMG_SIZE",         "224"))
FLASK_PORT     = int(os.environ.get("FLASK_PORT",       "5000"))
_cam_env       = os.environ.get("PHONE_CAM_URL", "0")
CAMERA_SRC     = int(_cam_env) if _cam_env.isdigit() else _cam_env
LABELS         = ["aphid", "armyworm", "mealybugs", "stem_borers", "weevil"]

state = {
    "moisture_raw": 0, "moisture_pct": 0,
    "pump_on": False, "last_pest": None,
    "last_pest_conf": 0.0, "alert_active": False,
    "detections_today": 0, "log": deque(maxlen=60),
    "cam_connected": False, "serial_connected": False,
}
state_lock = threading.Lock()
latest_frame = None
frame_lock   = threading.Lock()

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    e  = f"[{ts}] {msg}"
    with state_lock:
        state["log"].append(e)
    print(e)

def activate_deterrent():
    def _run():
        if GPIO_OK:
            GPIO.output(DETERRENT_PIN, GPIO.HIGH)
        log("DETERRENT: activated")
        time.sleep(DETERRENT_SECS)
        if GPIO_OK:
            GPIO.output(DETERRENT_PIN, GPIO.LOW)
        log("DETERRENT: off")
        with state_lock:
            state["alert_active"] = False
    threading.Thread(target=_run, daemon=True).start()

def serial_reader():
    if not SERIAL_OK:
        log("SERIAL: pyserial not installed"); return
    while True:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
            log(f"SERIAL: connected on {SERIAL_PORT}")
            with state_lock:
                state["serial_connected"] = True
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                if line.startswith("MOISTURE,"):
                    p = line.split(",")
                    if len(p) == 3:
                        with state_lock:
                            state["moisture_raw"] = int(p[1])
                            state["moisture_pct"] = int(p[2])
                elif line.startswith("PUMP:"):
                    with state_lock:
                        state["pump_on"] = (line == "PUMP:ON")
                    log(f"PUMP: {'ON' if state['pump_on'] else 'OFF'}")
                elif line.startswith("STATUS:"):
                    log(f"ARDUINO: {line[7:]}")
        except Exception as e:
            with state_lock:
                state["serial_connected"] = False
            log(f"SERIAL ERR: {e} — retry in 5s")
            time.sleep(5)

def camera_thread():
    global latest_frame
    log(f"CAMERA: connecting → {CAMERA_SRC}")
    cap = cv2.VideoCapture(CAMERA_SRC)
    if isinstance(CAMERA_SRC, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        log("CAMERA: failed to open"); return
    log("CAMERA: connected ✅")
    with state_lock:
        state["cam_connected"] = True
    while True:
        ret, frame = cap.read()
        if not ret:
            log("CAMERA: lost — reconnecting…")
            with state_lock:
                state["cam_connected"] = False
            cap.release(); time.sleep(2)
            cap = cv2.VideoCapture(CAMERA_SRC)
            if cap.isOpened():
                with state_lock:
                    state["cam_connected"] = True
            continue
        with frame_lock:
            latest_frame = frame.copy()
        time.sleep(0.04)

def detection_thread():
    if not TFLITE_OK:
        log("DETECTION: TFLite unavailable"); return
    if not os.path.exists(MODEL_PATH):
        log(f"DETECTION: no model at {MODEL_PATH}"); return
    interp = Interpreter(model_path=MODEL_PATH)
    interp.allocate_tensors()
    inp  = interp.get_input_details()
    outp = interp.get_output_details()
    log("DETECTION: model loaded ✅")
    while True:
        time.sleep(1.5)
        with frame_lock:
            if latest_frame is None: continue
            frame = latest_frame.copy()
        img = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        interp.set_tensor(inp[0]["index"], np.expand_dims(img, 0))
        interp.invoke()
        preds    = interp.get_tensor(outp[0]["index"])[0]
        top_idx  = int(np.argmax(preds))
        top_conf = float(preds[top_idx])
        pest     = LABELS[top_idx] if top_idx < len(LABELS) else "unknown"
        with state_lock:
            state["last_pest"]      = pest
            state["last_pest_conf"] = round(top_conf, 3)
        if top_conf >= CONF_THRESHOLD:
            log(f"PEST: {pest} ({top_conf:.1%})")
            with state_lock:
                state["detections_today"] += 1
                state["alert_active"] = True
            activate_deterrent()

app = Flask(__name__)

DASHBOARD_HTML = """<!DOCTYPE html>
<html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgroGuard</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#0f1923;color:#e8f5e9}
header{background:#1b5e20;padding:12px 20px;display:flex;align-items:center;gap:10px}
header h1{font-size:1.3rem}.live{background:#4caf50;border-radius:20px;padding:2px 9px;font-size:.72rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;padding:16px}
.card{background:#1a2634;border-radius:10px;padding:18px}
.card h3{color:#81c784;font-size:.75rem;text-transform:uppercase;margin-bottom:7px}
.big{font-size:2rem;font-weight:700}.sub{font-size:.75rem;color:#90a4ae;margin-top:3px}
.alert{background:#b71c1c;animation:pulse 1s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.65}}
.cam{padding:0 16px 16px}.cam h3{color:#81c784;margin-bottom:8px;font-size:.85rem}
img#feed{width:100%;max-width:640px;border-radius:8px;border:2px solid #2e7d32}
.logwrap{padding:0 16px 16px}.logwrap h3{color:#81c784;margin-bottom:8px;font-size:.85rem}
.logbox{background:#1a2634;border-radius:8px;padding:12px;font-family:monospace;font-size:.74rem;height:160px;overflow-y:auto}
.logbox p{border-bottom:1px solid #263238;padding:2px 0;color:#b0bec5}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:5px}
.on{background:#4caf50}.off{background:#f44336}
</style></head><body>
<header><span>🌿</span><h1>AgroGuard Dashboard</h1><span class="live">LIVE</span></header>
<div class="grid">
  <div class="card"><h3>💧 Soil Moisture</h3><div class="big" id="mpct">--%</div><div class="sub" id="mraw">ADC: --</div></div>
  <div class="card"><h3>⚙️ Water Pump</h3><div class="big" id="pump">--</div><div class="sub">Auto-irrigation</div></div>
  <div class="card" id="pc"><h3>🐛 Last Pest Scan</h3><div class="big" id="pname">--</div><div class="sub" id="pconf">Confidence: --</div></div>
  <div class="card"><h3>📊 Detections Today</h3><div class="big" id="dcnt">0</div><div class="sub">Pest alerts fired</div></div>
  <div class="card"><h3>🔌 Connections</h3>
    <div style="margin-top:8px"><span class="dot" id="dc"></span><span id="lc">Camera</span></div>
    <div style="margin-top:6px"><span class="dot" id="ds"></span><span id="ls">Arduino</span></div>
  </div>
</div>
<div class="cam"><h3>📷 Live Camera Feed</h3><img id="feed" src="/video_feed"></div>
<div class="logwrap"><h3>📋 System Log</h3><div class="logbox" id="lb"></div></div>
<script>
async function r(){
  try{
    const d=await(await fetch('/api/status')).json();
    document.getElementById('mpct').textContent=d.moisture_pct+'%';
    document.getElementById('mraw').textContent='ADC: '+d.moisture_raw;
    document.getElementById('pump').textContent=d.pump_on?'🟢 ON':'🔴 OFF';
    document.getElementById('pname').textContent=d.last_pest||'--';
    document.getElementById('pconf').textContent='Confidence: '+(d.last_pest_conf*100).toFixed(1)+'%';
    document.getElementById('dcnt').textContent=d.detections_today;
    document.getElementById('pc').className='card'+(d.alert_active?' alert':'');
    document.getElementById('dc').className='dot '+(d.cam_connected?'on':'off');
    document.getElementById('ds').className='dot '+(d.serial_connected?'on':'off');
    const lb=document.getElementById('lb');
    lb.innerHTML=d.log.map(l=>'<p>'+l+'</p>').join('');
    lb.scrollTop=lb.scrollHeight;
  }catch(e){}
}
setInterval(r,1500);r();
</script></body></html>"""

@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route("/api/status")
def api_status():
    with state_lock:
        return jsonify({**{k:v for k,v in state.items() if k!="log"},
                        "log": list(state["log"])})

def gen_frames():
    while True:
        with frame_lock:
            frame = latest_frame
        if frame is None:
            time.sleep(0.05); continue
        _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
        time.sleep(0.04)

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    log("AgroGuard Pi starting…")
    threading.Thread(target=serial_reader,    daemon=True).start()
    threading.Thread(target=camera_thread,    daemon=True).start()
    threading.Thread(target=detection_thread, daemon=True).start()
    import socket
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip = "0.0.0.0"
    log(f"Dashboard → http://{ip}:{FLASK_PORT}")
    app.run(host="0.0.0.0", port=FLASK_PORT, threaded=True)