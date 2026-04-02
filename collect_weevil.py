#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import os
import time
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from camera import Camera

output_dir = "dataset_new/weevil"
os.makedirs(output_dir, exist_ok=True)

current = len([f for f in os.listdir(output_dir) if f.endswith('.jpg')])
target = 120
needed = max(0, target - current)

if needed <= 0:
    print(f"Already have {current} weevil images")
    exit()

print(f"Collecting weevil images... Need {needed} more")
print("Place weevil in front of camera")
print("Capturing every 2 seconds. Press Ctrl+C to stop")

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
        filename = f"weevil_{timestamp}_{captured:04d}.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, frame)
        
        captured += 1
        print(f"[{captured}/{needed}] Saved: {filename}")
        time.sleep(2)
        
except KeyboardInterrupt:
    pass
finally:
    camera.stop()

print(f"Done! Total weevil images: {current + captured}")
