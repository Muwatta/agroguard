import os
from services.detection import add_pest_event
from datetime import datetime

CAPTURE_DIR = os.path.join(os.getcwd(), "static/captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)

def save_snapshot(frame, pest_type, deterrent=False):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{pest_type}_{timestamp}.jpg"
    path = os.path.join(CAPTURE_DIR, filename)
    cv2.imwrite(path, frame)
    add_pest_event(pest_type, f"/static/captures/{filename}", deterrent)
    return path

