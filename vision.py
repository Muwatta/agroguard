import numpy as np
import cv2
import os
import time

CAPTURE_DIR = "static/captures"

prev_frame = None


def detect_motion(camera, min_area=500, learning_rate=0.01):
    """Detect motion using frame differencing on camera stream."""
    global prev_frame

    frame_bytes = camera.get_frame() if camera else None
    if frame_bytes is None:
        return None, False

    nparr = np.frombuffer(frame_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        return None, False

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if prev_frame is None:
        prev_frame = gray.copy()
        return frame, False

    frame_delta = cv2.absdiff(prev_frame, gray)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion = False
    for c in contours:
        if cv2.contourArea(c) < min_area:
            continue
        motion = True
        break

    # Keep a stable background reference with simple assignment
    # (avoid accumulateWeighted issues in some OpenCV builds)
    prev_frame = gray.copy()

    return frame, motion


def save_capture(frame):
    """Save frame to disk."""
    os.makedirs(CAPTURE_DIR, exist_ok=True)

    timestamp = int(time.time())
    filename = f"cap_{timestamp}.jpg"
    filepath = os.path.join(CAPTURE_DIR, filename)

    cv2.imwrite(filepath, frame)
    return filepath, timestamp