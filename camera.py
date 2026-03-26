#!/usr/bin/env python3
"""
Camera Module - Optimized for Windows with DirectShow
No MSMF warnings, works with laptop webcam
"""

import cv2
import numpy as np
import threading
import time
import os

# Force DirectShow backend on Windows
os.environ['OPENCV_VIDEOIO_PRIORITY_BACKEND'] = 'DSHOW'

class Camera:
    def __init__(self, source=0):
        """Initialize camera - source 0 for laptop webcam"""
        self.source = source
        self.camera = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        self.error_count = 0
        
        # Open camera with DirectShow (no MSMF warnings)
        self._open_camera()
        
        # Set properties
        if self.camera and self.camera.isOpened():
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            print(f"✅ Camera initialized (DirectShow)")
        else:
            print("⚠️ Camera failed - will use test pattern")
    
    def _open_camera(self):
        """Open camera with proper backend"""
        # Try DirectShow first (Windows)
        self.camera = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
        
        if not self.camera.isOpened():
            # Fallback to default
            self.camera = cv2.VideoCapture(self.source)
    
    def start(self):
        """Start capture thread"""
        if not self.running and self.camera and self.camera.isOpened():
            self.running = True
            threading.Thread(target=self._update, daemon=True).start()
            print("📹 Camera streaming started")
    
    def _update(self):
        """Capture frames continuously"""
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
            except Exception as e:
                pass  # Silent error handling
            time.sleep(0.033)  # ~30 FPS
    
    def _reconnect(self):
        """Try to reconnect"""
        if self.camera:
            self.camera.release()
        time.sleep(0.5)
        self._open_camera()
        self.error_count = 0
    
    def get_frame(self):
        """Get current frame as JPEG bytes"""
        with self.lock:
            if self.frame is not None:
                ret, jpeg = cv2.imencode('.jpg', self.frame, 
                                        [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                if ret:
                    return jpeg.tobytes()
        
        # Return test pattern if no frame
        return self._get_test_pattern()
    
    def _get_test_pattern(self):
        """Generate test pattern when camera fails"""
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(blank, "AgroGuard AI", (200, 200), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(blank, "Camera Test Pattern", (150, 280), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(blank, time.strftime("%H:%M:%S"), (250, 350), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        ret, jpeg = cv2.imencode('.jpg', blank)
        return jpeg.tobytes() if ret else None
    
    def stop(self):
        """Stop camera"""
        self.running = False
        if self.camera:
            self.camera.release()
    
    def __del__(self):
        self.stop()

def gen_frames(camera):
    """Generator for video streaming"""
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.033)