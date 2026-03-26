# vision.py - dummy version for testing
import numpy as np
import cv2
import os
import time

def detect_motion():
    """Dummy motion detection - returns a blank frame with random motion"""
    # Create a blank image
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Simulate motion detection (True 30% of the time)
    motion = np.random.random() > 0.7
    
    if motion:
        # Draw something on the frame to simulate detection
        cv2.circle(frame, (320, 240), 50, (0, 255, 0), -1)
    
    return frame, motion

def save_capture(frame):
    """Save frame to disk"""
    capture_dir = "static/captures"
    os.makedirs(capture_dir, exist_ok=True)
    
    timestamp = int(time.time())
    filename = f"cap_{timestamp}.jpg"
    filepath = os.path.join(capture_dir, filename)
    
    cv2.imwrite(filepath, frame)
    return filepath, timestamp