#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import os
import time
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from camera import Camera

output_dir = "dataset_new/armyworm"
os.makedirs(output_dir, exist_ok=True)

current = len([f for f in os.listdir(output_dir) if f.endswith('.jpg')])
target = 200  # Let's get even more
needed = max(0, target - current)

print(f"Armyworm images: {current}/{target}")
print(f"Need {needed} more images")
print("\nPlace armyworm in front of camera")
print("Capturing every 2 seconds. Press Ctrl+C to stop\n")

camera = Camera(0)
camera.start()
time.sleep(2)

captured = 0
try:
    while captured < needed:
        frame_bytes = camera.get_frame()
        if frame_bytes is None:
            continue
        
        import numpy as np
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            continue
        
        timestamp = int(time.time())
        filename = f"armyworm_{timestamp}_{captured:04d}.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, frame)
        
        captured += 1
        total = current + captured
        print(f"[{captured}/{needed}] Saved: {filename} (Total: {total})")
        time.sleep(2)
        
except KeyboardInterrupt:
    pass
finally:
    camera.stop()

print(f"\nDone! Total armyworm: {current + captured}")
