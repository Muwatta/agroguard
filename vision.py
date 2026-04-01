import numpy as np
import cv2
import os
import time

CAPTURE_DIR = "static/captures"


def detect_motion(camera, min_area=500, learning_rate=0.01):
    """Detect motion using frame differencing on camera stream."""
    # Get frame from camera object
    frame_bytes = camera.get_frame() if camera else None
    if frame_bytes is None:
        return None, False

    nparr = np.frombuffer(frame_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        return None, False

    # Ensure frame has consistent size (fix potential dimension issues)
    # Use a fixed size for motion detection
    frame = cv2.resize(frame, (640, 480))
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Store prev_frame as an attribute of the camera object
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

    motion = False
    for c in contours:
        if cv2.contourArea(c) < min_area:
            continue
        motion = True
        # Draw bounding box on frame
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        break

    # Update previous frame
    camera.prev_frame = gray.copy()

    return frame, motion


def save_capture(frame):
    """Save frame to disk."""
    os.makedirs(CAPTURE_DIR, exist_ok=True)

    timestamp = int(time.time())
    filename = f"cap_{timestamp}.jpg"
    filepath = os.path.join(CAPTURE_DIR, filename)

    cv2.imwrite(filepath, frame)
    return filepath, timestamp