import cv2
import os
import numpy as np

input_dir = "dataset_new/armyworm"
output_dir = "dataset_new/armyworm_augmented"
os.makedirs(output_dir, exist_ok=True)

# Copy original images
for img_file in os.listdir(input_dir):
    if img_file.endswith('.jpg'):
        img = cv2.imread(os.path.join(input_dir, img_file))
        
        # Save original
        cv2.imwrite(os.path.join(output_dir, img_file), img)
        
        # Create variations
        for i, angle in enumerate([90, 180, 270]):
            rotated = cv2.rotate(img, i)
            name = img_file.replace('.jpg', f'_rot{i}.jpg')
            cv2.imwrite(os.path.join(output_dir, name), rotated)
        
        # Flip horizontally
        flipped = cv2.flip(img, 1)
        name = img_file.replace('.jpg', '_flip.jpg')
        cv2.imwrite(os.path.join(output_dir, name), flipped)

print(f"Augmented images saved to {output_dir}")
print("Now copy them back or use this folder for training")
