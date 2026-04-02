#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import requests

output_dir = "dataset_new/armyworm"
os.makedirs(output_dir, exist_ok=True)

current = len([f for f in os.listdir(output_dir) if f.endswith('.jpg')])
target = 200  # Get even more
needed = max(0, target - current)

print(f"Current: {current}, Need: {needed}")

# Use a free image API
url = "https://source.unsplash.com/featured/?armyworm"

downloaded = 0
for i in range(needed):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            filename = f"armyworm_online_{int(time.time())}_{i:04d}.jpg"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            downloaded += 1
            print(f"[{downloaded}/{needed}] Saved: {filename}")
        time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")

print(f"Done! Total armyworm: {current + downloaded}")
