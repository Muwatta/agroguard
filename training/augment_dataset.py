import os
import cv2
import albumentations as A

def augment_dataset(target_per_class=500):
    transform = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.3),
        A.RandomRotate90(p=0.5),
        A.Rotate(limit=45, p=0.8),
        A.ShiftScaleRotate(shift_limit=0.2, scale_limit=0.2, rotate_limit=30, p=0.8),
        A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.8),
        A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.5),
        A.Blur(blur_limit=3, p=0.3),
    ])
    
    base_dir = 'dataset'
    aug_dir = 'dataset_augmented'
    os.makedirs(aug_dir, exist_ok=True)
    
    for class_name in os.listdir(base_dir):
        class_path = os.path.join(base_dir, class_name)
        if not os.path.isdir(class_path):
            continue
            
        aug_class_path = os.path.join(aug_dir, class_name)
        os.makedirs(aug_class_path, exist_ok=True)
        
        images = [f for f in os.listdir(class_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        print(f"Augmenting {class_name}: {len(images)} → {target_per_class}")
        
        # Copy originals
        for img_name in images:
            src = os.path.join(class_path, img_name)
            dst = os.path.join(aug_class_path, f"orig_{img_name}")
            img = cv2.imread(src)
            if img is not None:
                cv2.imwrite(dst, img)
        
        # Generate augmented
        current = len(images)
        aug_count = 0
        while current < target_per_class:
            for img_name in images:
                if current >= target_per_class:
                    break
                img = cv2.imread(os.path.join(class_path, img_name))
                if img is not None:
                    aug_img = transform(image=img)['image']
                    cv2.imwrite(os.path.join(aug_class_path, f"aug_{aug_count}_{img_name}"), aug_img)
                    current += 1
                    aug_count += 1

if __name__ == '__main__':
    augment_dataset()