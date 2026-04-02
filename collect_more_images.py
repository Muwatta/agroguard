import cv2
import os
import time
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from camera import Camera

def get_current_counts():
    """Get current image counts per class"""
    counts = {}
    for class_name in ['aphid', 'armyworm', 'mealybugs', 'none', 'stem_borers', 'weevil']:
        class_dir = f"dataset_new/{class_name}"
        if os.path.exists(class_dir):
            count = len([f for f in os.listdir(class_dir) if f.endswith('.jpg')])
            counts[class_name] = count
        else:
            counts[class_name] = 0
    return counts

def collect_images(class_name, target_count=120):
    """Collect images for a specific class"""
    output_dir = f"dataset_new/{class_name}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get current count
    current = len([f for f in os.listdir(output_dir) if f.endswith('.jpg')])
    needed = max(0, target_count - current)
    
    if needed <= 0:
        print(f"‚úÖ {class_name} already has {current} images (target: {target_count})")
        return
    
    print(f"\n{'='*60}")
    print(f"Ì≥∏ Collecting {class_name.upper()} images")
    print(f"Current: {current} | Target: {target_count} | Needed: {needed}")
    print(f"{'='*60}")
    print("Press SPACE to capture, 'q' to quit")
    print("Press 's' to skip this class")
    print(f"Saving to: {output_dir}")
    
    # Initialize camera
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
            
            # Add instructions on frame
            cv2.putText(frame, f"Class: {class_name}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Captured: {captured}/{needed}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "SPACE: Capture | q: Quit | s: Skip", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display
            cv2.imshow(f'Capture {class_name}', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACE
                timestamp = int(time.time())
                filename = f"{class_name}_{timestamp}_{captured:04d}.jpg"
                filepath = os.path.join(output_dir, filename)
                cv2.imwrite(filepath, frame)
                print(f"‚úÖ [{captured+1}/{needed}] Saved: {filename}")
                captured += 1
            elif key == ord('q'):
                break
            elif key == ord('s'):
                print(f"‚è≠Ô∏è Skipping {class_name}")
                break
                
    except KeyboardInterrupt:
        print("\n‚ö†Ô∏è Interrupted")
    finally:
        cv2.destroyAllWindows()
        camera.stop()
    
    print(f"\nÌ≥ä {class_name}: Added {captured} new images")
    print(f"   Total now: {current + captured}\n")

def main():
    print("=" * 60)
    print("Ì≥∏ AGROGUARD - TRAINING DATA COLLECTION")
    print("=" * 60)
    
    # Show current counts
    print("\nCurrent dataset sizes:")
    counts = get_current_counts()
    for class_name, count in counts.items():
        target = 120
        status = "‚úÖ" if count >= target else "‚ö†Ô∏è"
        print(f"  {status} {class_name}: {count}/{target} images")
    
    print("\n" + "=" * 60)
    print("We'll collect images for classes that need more data")
    print("For each class, place the pest in front of camera")
    print("Capture from different angles and lighting conditions")
    print("=" * 60)
    
    input("\nPress Enter to start collecting...")
    
    # Classes to collect (prioritize those with fewest images)
    classes_to_collect = [
        ('weevil', 120),
        ('armyworm', 120),
        ('none', 100),
        ('aphid', 120),
        ('mealybugs', 120),
        ('stem_borers', 120)
    ]
    
    for class_name, target in classes_to_collect:
        collect_images(class_name, target)
        
        # Ask if user wants to continue
        response = input(f"\nContinue to next class? (y/n): ").strip().lower()
        if response != 'y':
            print("Stopping collection")
            break
    
    # Show final counts
    print("\n" + "=" * 60)
    print("FINAL DATASET SIZES:")
    print("=" * 60)
    final_counts = get_current_counts()
    for class_name, count in final_counts.items():
        target = 120
        status = "‚úÖ" if count >= target else "‚ö†Ô∏è"
        print(f"  {status} {class_name}: {count}/{target} images")
    
    print("\n‚úÖ Collection complete!")
    print("Now run: python retrain_with_none.py")
    print("Then restart: python app.py")

if __name__ == "__main__":
    main()
