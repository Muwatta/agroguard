import cv2
import os
import time

def capture_none_samples(output_dir="dataset_augmented/none", num_samples=50):
    """Capture images of background/empty scenes (headless version)"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Try different camera indices
    camera_index = 0
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)  # Use DirectShow on Windows
    
    if not cap.isOpened():
        print(f"❌ Could not open camera {camera_index}")
        return
    
    print(f"✅ Camera opened successfully")
    print("📸 Capturing 'none' class images...")
    print("The script will capture images every 2 seconds automatically")
    print("Press Ctrl+C to stop early")
    
    count = 0
    try:
        while count < num_samples:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to capture frame")
                continue
            
            # Save frame
            timestamp = int(time.time())
            filename = f"none_{timestamp}_{count:04d}.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, frame)
            
            print(f"✅ Saved: {filename} ({count+1}/{num_samples})")
            count += 1
            
            # Wait 2 seconds between captures
            time.sleep(2)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Stopped early. Captured {count}/{num_samples} images")
    
    cap.release()
    print(f"\n✅ Done! Captured {count} 'none' class images in {output_dir}")
    
    # Show where to put the images
    print(f"\n📁 Images saved to: {os.path.abspath(output_dir)}")
    print("Now you can retrain your model with these 'none' images")

def capture_manual_mode(output_dir="dataset_augmented/none", num_samples=30):
    """Manual capture mode - press Enter to capture, q to quit"""
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("❌ Could not open camera")
        return
    
    print("📸 Manual capture mode")
    print("Press ENTER to capture current frame")
    print("Press 'q' to quit")
    
    count = 0
    while count < num_samples:
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Save frame when Enter is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter key
            filename = f"none_{count:04d}.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, frame)
            print(f"✅ Saved: {filename} ({count+1}/{num_samples})")
            count += 1
        elif key == ord('q'):
            break
    
    cap.release()
    print(f"\n✅ Captured {count} images")

if __name__ == "__main__":
    print("Select capture mode:")
    print("1. Automatic (captures every 2 seconds)")
    print("2. Manual (press Enter to capture)")
    
    mode = input("Enter mode (1 or 2): ").strip()
    
    if mode == "1":
        num = input("Number of images to capture (default 50): ").strip()
        num = int(num) if num else 50
        capture_none_samples(num_samples=num)
    elif mode == "2":
        num = input("Number of images to capture (default 30): ").strip()
        num = int(num) if num else 30
        capture_manual_mode(num_samples=num)
    else:
        print("Invalid mode. Using automatic mode.")
        capture_none_samples()