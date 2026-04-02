#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import glob

def rename_images_in_folder(folder_path, class_name):
    """Rename all images in folder to sequential numbers (01, 02, 03...)"""
    # Get all image files
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    images = []
    for ext in extensions:
        images.extend(glob.glob(os.path.join(folder_path, ext)))
    
    if not images:
        print(f"  No images found in {class_name}")
        return
    
    # Sort images by modification time or name
    images.sort(key=os.path.getmtime)
    
    # Rename each image
    renamed_count = 0
    for idx, old_path in enumerate(images, start=1):
        # Create new filename with 2-digit numbering
        new_filename = f"{class_name}_{idx:02d}.jpg"
        new_path = os.path.join(folder_path, new_filename)
        
        # If the file already has the correct name, skip
        if os.path.basename(old_path) == new_filename:
            continue
        
        # Rename the file
        try:
            os.rename(old_path, new_path)
            renamed_count += 1
            print(f"    {os.path.basename(old_path)} -> {new_filename}")
        except Exception as e:
            print(f"    Error renaming {old_path}: {e}")
    
    print(f"  {class_name}: Renamed {renamed_count} files (Total: {len(images)})")

def main():
    print("=" * 60)
    print("RENAMING DATASET IMAGES")
    print("=" * 60)
    
    # Base directory
    base_dir = "dataset_new"
    
    # Get all class folders
    class_folders = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    class_folders.sort()
    
    print(f"\nFound {len(class_folders)} classes:\n")
    
    for class_name in class_folders:
        folder_path = os.path.join(base_dir, class_name)
        print(f"\nProcessing {class_name.upper()}...")
        rename_images_in_folder(folder_path, class_name)
    
    print("\n" + "=" * 60)
    print("RENAMING COMPLETE!")
    print("=" * 60)
    
    # Show summary
    print("\nFinal dataset structure:")
    for class_name in class_folders:
        folder_path = os.path.join(base_dir, class_name)
        count = len(glob.glob(os.path.join(folder_path, "*.jpg")))
        print(f"  {class_name}: {count} images (01-{count:02d})")

if __name__ == "__main__":
    main()
