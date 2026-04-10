#!/usr/bin/env python3
"""
Camera Module - Supports local webcam AND phone IP camera
"""

import cv2
import numpy as np
import threading
import time

class Camera:
    def __init__(self, source=0):
        self.source = source
        self.camera = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        self.error_count = 0
        
        # Check if source is a URL (phone camera)
        if isinstance(source, str) and ('http' in source or '://' in source):
            print(f"📱 Connecting to phone camera: {source}")
            self.camera = cv2.VideoCapture(source)
        else:
            print(f"💻 Using local camera (source={source})")
            self.camera = cv2.VideoCapture(source)
        
        if not self.camera.isOpened():
            print("⚠️ Camera failed - will use test pattern")
        else:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            print(f"✅ Camera initialized")
    
    def start(self):
        if not self.running and self.camera and self.camera.isOpened():
            self.running = True
            threading.Thread(target=self._update, daemon=True).start()
            print("📹 Camera streaming started")
    
    def _update(self):
        while self.running:
            try:
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    with self.lock:
                        self.frame = frame
                    self.error_count = 0
                else:
                    self.error_count += 1
                    if self.error_count > 5:
                        print("Camera: Reconnecting...")
                        self._reconnect()
            except:
                pass
            time.sleep(0.033)
    
    def _reconnect(self):
        if self.camera:
            self.camera.release()
        time.sleep(0.5)
        if isinstance(self.source, str) and ('http' in self.source or '://' in self.source):
            self.camera = cv2.VideoCapture(self.source)
        else:
            self.camera = cv2.VideoCapture(self.source)
        self.error_count = 0
    
    def get_frame(self):
        with self.lock:
            if self.frame is not None:
                ret, jpeg = cv2.imencode('.jpg', self.frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                if ret:
                    return jpeg.tobytes()
        return self._get_test_pattern()
    
    def _get_test_pattern(self):
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(blank, "AgroGuard AI", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(blank, "Camera Test Pattern", (150, 280), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(blank, time.strftime("%H:%M:%S"), (250, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        ret, jpeg = cv2.imencode('.jpg', blank)
        return jpeg.tobytes() if ret else None
    
    def stop(self):
        self.running = False
        if self.camera:
            self.camera.release()
    
    def __del__(self):
        self.stop()

def gen_frames(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.033)