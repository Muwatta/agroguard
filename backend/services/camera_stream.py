import os
from datetime import datetime

# Placeholder: list to store pest detections
pest_events = []

def get_pest_events():
    # Return last 10 events for dashboard
    return pest_events[-10:]

def add_pest_event(pest_type, image_path, deterrent=False):
    pest_events.append({
        "pest": pest_type,
        "time": datetime.now().strftime("%H:%M:%S"),
        "image": image_path,
        "deterrent": deterrent
    })