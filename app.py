# At the top of app.py, add/verify these imports
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
            print("⚠️ Warning: Could not load face cascade")
        else:
            print("✅ Face cascade loaded")
    return face_cascade

def contains_face(frame):
    """Detect if frame contains a human face"""
    try:
        cascade = get_face_cascade()
        if cascade.empty():
            return False
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(50, 50)
        )
        
        if len(faces) > 0:
            print(f"👤 Detected {len(faces)} face(s) - skipping pest classification")
            return True
        return False
    except Exception as e:
        print(f"⚠️ Face detection error: {e}")
        return False

def agroguard_loop():
    """Main detection loop with improved error handling"""
    global last_sprinkler_time
    
    try:
        # Call detect_motion with camera object
        frame, motion = detect_motion(camera)
        
        if frame is None:
            # print("Warning: No frame received from camera")
            return
            
        if not motion:
            return
            
        # Check if the motion is caused by a human face
        if contains_face(frame):
            print("🚫 Motion detected but contains human face - ignoring")
            return

        # Save captured frame
        img_path, ts = save_capture(frame)
        print(f"Captured: {os.path.basename(img_path)}")

        # Classify the pest
        pest, conf = classify(img_path)
        print(f"Classified: {pest} ({conf:.2f})")

        from config import CONF_THRESHOLD

        # Skip unidentified, none class, or low confidence detections
        if pest == 'unidentified' or pest == 'none' or conf < CONF_THRESHOLD:
            if pest == 'none':
                print(f"🚫 Classified as 'none' (background/no pest)")
            else:
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
        
        # Critical pest response with cooldown
        critical_pests = ["armyworm", "aphid", "mealybugs", "stem_borers", "weevil"]
        if pest in critical_pests and conf > 0.8:
            print(f"⚠️ Critical pest detected - activating defenses!")
            
            # Check cooldown to prevent constant sprinkling
            current_time = datetime.now()
            if last_sprinkler_time is None or (current_time - last_sprinkler_time).seconds > SPRINKLER_COOLDOWN:
                hardware.sprinkler_on(10)
                if arduino.connected:
                    arduino.sprinkler_on(10)
                last_sprinkler_time = current_time
                print(f"💦 Sprinkler activated (cooldown: {SPRINKLER_COOLDOWN}s)")
            else:
                seconds_remaining = SPRINKLER_COOLDOWN - (current_time - last_sprinkler_time).seconds
                print(f"⏱️ Sprinkler in cooldown ({seconds_remaining}s remaining)")
        
        print(f"✅ ALERT: {pest} detected with {conf:.2f} confidence")
        
    except Exception as e:
        print(f"Error in detection loop: {e}")
        traceback.print_exc()

# ... rest of your routes ...

if __name__ == "__main__":
    def detection_thread():
        print("Detection loop started")
        while True:
            try:
                agroguard_loop()
                time.sleep(1)  # Wait 1 second between detections
            except Exception as e:
                print(f"Error in detection thread: {e}")
                traceback.print_exc()
                time.sleep(2)
    
    # Start detection thread
    threading.Thread(target=detection_thread, daemon=True).start()
    print("Server starting on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)