import cv2
import time
import os
from config import CAMERA_URL, CAPTURE_DIR

cap = cv2.VideoCapture(CAMERA_URL)
bg = cv2.createBackgroundSubtractorMOG2()

def detect_motion():
    ret, frame = cap.read()
    if not ret:
        return None, False

    mask = bg.apply(frame)
    motion = mask.sum() > 500000

    return frame, motion


def save_capture(frame):
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(CAPTURE_DIR, f"{ts}.jpg")
    cv2.imwrite(path, frame)
    return path, ts