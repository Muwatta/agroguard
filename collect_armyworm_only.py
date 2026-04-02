#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import os
import time
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from camera import Camera

print("=" * 60)
print("ARMYWORM IMAGE COLLECTOR")
print("=" * 60)
print("Place armyworm image in front of camera")
print("Press SPACE to capture, 'q' to quit")
print()

output_dir = "dataset_new/armyworm"
os.makedirs(output_dir, exist_ok=True)

current = len([f for f in os.listdir(output_dir) if f.endswith('.jpg')])
print(f"Current armyworm images: {current}")
print(f"Target: 120")
print()

camera = Camera(0)
camera.start()
time.sleep(2)

count = 0
try:
    while True:
        frame_bytes = camera.get_frame()
        if frame_bytes is None:
            continue
        
        import numpy as np
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            continue
        
        cv2.putText(frame, f"Armyworm: {current + count}/120", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "SPACE: Capture | q: Quit", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow('Capture Armyworm', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACE
            timestamp = int(time.time())
            filename = f"armyworm_{timestamp}_{count:04d}.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, frame)
            print(f"[{count+1}/84] Saved: {filename}")
            count += 1
            if count >= 84:
                print("Reached target! Enough armyworm images.")
                break
        elif key == ord('q'):
            break

except KeyboardInterrupt:
    pass
finally:
    cv2.destroyAllWindows()
    camera.stop()

print(f"\nDone! Total armyworm images: {current + count}")
