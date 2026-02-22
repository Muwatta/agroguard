import cv2
import serial
import time
import os
from flask import Flask, render_template, Response

app = Flask(__name__)

# CONFIG: Use your phone's IP address
PHONE_CAM_URL = "http://192.168.1.15:8080/video" 
if not os.path.exists('static/captures'): os.makedirs('static/captures')

# AUTOMATION TRACKING
pest_visit_count = 0
last_detection_time = 0
COOLDOWN = 10  # Seconds to wait before counting a "new" visit
THRESHOLD = 5000 # Motion sensitivity (smaller = more sensitive)

try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
except:
    ser = None

def gen_frames():
    global pest_visit_count, last_detection_time
    cap = cv2.VideoCapture(PHONE_CAM_URL)
    # Background Subtractor MOG2: The "AI" that learns the background
    fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)

    while True:
        success, frame = cap.read()
        if not success: break
        
        # 1. Apply AI motion mask
        fgmask = fgbg.apply(frame)
        motion_score = cv2.countNonZero(fgmask)
        
        # 2. Automation Logic
        if motion_score > THRESHOLD:
            now = time.time()
            if now - last_detection_time > COOLDOWN:
                pest_visit_count += 1
                last_detection_time = now
                
                # TRIGGER: After 2nd visit
                if pest_visit_count >= 2:
                    img_path = f"static/captures/pest_{int(now)}.jpg"
                    cv2.imwrite(img_path, frame)
                    if ser: ser.write(b'P') # 'P' for Panic Alarm (20s)
        
        # 3. Add visual data overlay for the dashboard
        cv2.putText(frame, f"AI DETECTIONS: {pest_visit_count}", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    # Read Sensors from Arduino
    data = {"temp": "0", "hum": "0", "soil": "0", "gas": "0"}
    if ser and ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        p = line.split(',')
        if len(p) == 4: data = {"temp": p[0], "hum": p[1], "soil": p[2], "gas": p[3]}

    # Get Captured Photos
    pics = [f for f in os.listdir('static/captures') if f.endswith('.jpg')]
    pics.sort(reverse=True) # Show latest captures first

    return render_template('index.html', data=data, pics=pics[:4], count=pest_visit_count)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
