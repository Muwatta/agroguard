#!/usr/bin/env python
"""Display system information"""
import platform
import os
import sys
import cv2
import tensorflow as tf

print("=" * 60)
print("AGROGUARD SYSTEM INFORMATION")
print("=" * 60)

print(f"\nÌ∂•Ô∏è SYSTEM:")
print(f"   OS: {platform.system()} {platform.release()}")
print(f"   Python: {platform.python_version()}")
print(f"   Machine: {platform.machine()}")

print(f"\nÌ≥∏ OPENCV:")
print(f"   Version: {cv2.__version__}")

print(f"\nÌ∑† TENSORFLOW:")
print(f"   Version: {tf.__version__}")

print(f"\nÌ≥Å PATHS:")
print(f"   Current: {os.getcwd()}")
print(f"   Model: {os.path.exists('model/pest_model.tflite') and '‚úÖ' or '‚ùå'} model/pest_model.tflite")
print(f"   Dataset: {os.path.exists('dataset_new') and '‚úÖ' or '‚ùå'} dataset_new/")

# Count images in dataset
if os.path.exists('dataset_new'):
    print(f"\nÌ≥ä DATASET STATS:")
    for class_dir in os.listdir('dataset_new'):
        class_path = os.path.join('dataset_new', class_dir)
        if os.path.isdir(class_path):
            count = len([f for f in os.listdir(class_path) if f.endswith(('.jpg', '.png'))])
            print(f"   {class_dir}: {count} images")

print("\n" + "=" * 60)
