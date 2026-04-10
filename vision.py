import numpy as np
import cv2
import os
import time

CAPTURE_DIR = "static/captures"

# Load face cascade once
face_cascade = None

def get_face_cascade():
    """Load face cascade classifier"""
    global face_cascade
    if face_cascade is None:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        if face_cascade.empty():
            print("⚠️ Warning: Could not load face cascade")
        else:
            print("✅ Face cascade loaded")
    return face_cascade

def detect_faces(frame):
    """Detect faces in frame"""
    try:
        cascade = get_face_cascade()
        if cascade.empty():
            return []
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return faces
    except Exception as e:
        print(f"⚠️ Face detection error: {e}")
        return []

def detect_motion(camera, min_area=500, learning_rate=0.01, motion_history=3):
    """Detect motion using frame differencing with face detection"""
    # Get frame from camera object
    frame_bytes = camera.get_frame() if camera else None
    if frame_bytes is None:
        return None, False

    nparr = np.frombuffer(frame_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        return None, False

    # Ensure frame has consistent size
    frame = cv2.resize(frame, (640, 480))
    
    # Check for faces FIRST (before motion detection)
    faces = detect_faces(frame)
    if len(faces) > 0:
        print(f"👤 Detected {len(faces)} face(s) - marking as no motion")
        # Draw rectangles around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, "FACE", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # Return frame with face detection but no motion trigger
        return frame, False
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Initialize motion history
    if not hasattr(camera, 'motion_history'):
        camera.motion_history = []
    if not hasattr(camera, 'prev_frame') or camera.prev_frame is None:
        camera.prev_frame = gray.copy()
        return frame, False

    # Ensure previous frame has the same dimensions
    if camera.prev_frame.shape != gray.shape:
        camera.prev_frame = cv2.resize(camera.prev_frame, (gray.shape[1], gray.shape[0]))

    # Compute absolute difference
    frame_delta = cv2.absdiff(camera.prev_frame, gray)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Calculate total motion area
    motion_contours = []
    
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        motion_contours.append(c)
        
        # Draw bounding box on frame
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Determine if motion is significant
    motion_detected = len(motion_contours) > 0
    
    # Add to motion history (for persistence)
    camera.motion_history.append(motion_detected)
    if len(camera.motion_history) > motion_history:
        camera.motion_history.pop(0)
    
    # Require multiple frames of motion to trigger
    persistent_motion = sum(camera.motion_history) >= (motion_history // 2 + 1)
    
    # Update previous frame
    camera.prev_frame = gray.copy()

    return frame, persistent_motion

def save_capture(frame):
    """Save frame to disk."""
    os.makedirs(CAPTURE_DIR, exist_ok=True)

    timestamp = int(time.time())
    filename = f"cap_{timestamp}.jpg"
    filepath = os.path.join(CAPTURE_DIR, filename)

    cv2.imwrite(filepath, frame)
    return filepath, timestamp