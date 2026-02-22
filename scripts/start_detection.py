import cv2
from backend.classifier import detect_pest
from backend.storage import save_snapshot
from backend.services.deterrent import trigger_buzzer

CAMERA_URL = "http://10.35.236.252:8080/video"

cap = cv2.VideoCapture(CAMERA_URL)

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    pest = detect_pest(frame)
    if pest:
        # Trigger deterrent for 20-second pulse (adjust as needed)
        trigger_buzzer(duration=2)
        save_snapshot(frame, pest, deterrent=True)