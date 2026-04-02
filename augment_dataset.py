#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import os
import numpy as np
from pathlib import Path

def augment_images(input_dir, output_dir=None, target_count=100):
    """Augment images to reach target count"""
    if output_dir is None:
        output_dir = input_dir
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get existing images
    images = [f for f in os.listdir(input_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    current_count = len(images)
    
    if current_count >= target_count:
        print(f"  Already have {current_count} images (target: {target_count})")
        return current_count
    
    needed = target_count - current_count
    print(f"  Current: {current_count}, Target: {target_count}, Need: {needed} augmented images")
    
    # Augmentation functions
    def rotate_image(img, angle):
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(img, matrix, (w, h))
    
    def adjust_brightness(img, value):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = cv2.add(hsv[:, :, 2], value)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    def add_noise(img):
        noise = np.random.randint(0, 20, img.shape, dtype='uint8')
        return cv2.add(img, noise)
    
    generated = 0
    idx = 0
    
    while generated < needed and idx < len(images):
        img_path = os.path.join(input_dir, images[idx])
        img = cv2.imread(img_path)
        
        if img is None:
            idx += 1
            continue
        
        # Generate variations
        variations = [
            ('_rot90', lambda x: cv2.rotate(x, cv2.ROTATE_90_CLOCKWISE)),
            ('_rot180', lambda x: cv2.rotate(x, cv2.ROTATE_180)),
            ('_rot270', lambda x: cv2.rotate(x, cv2.ROTATE_90_COUNTERCLOCKWISE)),
            ('_flip_h', lambda x: cv2.flip(x, 1)),
            ('_flip_v', lambda x: cv2.flip(x, 0)),
            ('_bright', lambda x: adjust_brightness(x, 30)),
            ('_dark', lambda x: adjust_brightness(x, -30)),
            ('_noise', lambda x: add_noise(x)),
        ]
        
        for suffix, transform in variations:
            if generated >= needed:
                break
            
            augmented = transform(img)
            name = Path(img_path).stem + suffix + Path(img_path).suffix
            out_path = os.path.join(output_dir, name)
            cv2.imwrite(out_path, augmented)
            generated += 1
            
        idx += 1
    
    total = current_count + generated
    print(f"  Created {generated} augmented images")
    print(f"  Total: {total}")
    return total

def augment_all_classes(target_counts=None):
    """Augment all pest classes"""
    if target_counts is None:
        target_counts = {
            'aphid': 100,
            'armyworm': 100,
            'mealybugs': 100,
            'none': 100,
            'stem_borers': 100,
            'weevil': 100
        }
    
    print("=" * 60)
    print("AUGMENTING DATASET")
    print("=" * 60)
    
    for class_name, target in target_counts.items():
        class_dir = f"dataset_new/{class_name}"
        if os.path.exists(class_dir):
            print(f"\n{class_name.upper()}:")
            augment_images(class_dir, class_dir, target)
    
    print("\n" + "=" * 60)
    print("AUGMENTATION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    augment_all_classes()
