import json
import os
import time
from datetime import datetime

STORAGE_FILE = "events.json"

def log_event(timestamp, pest, confidence, image_path, advice):
    """Log a pest detection event"""
    # Store as list: [timestamp, pest, confidence, image_path, advice]
    event = [
        timestamp,
        pest,
        confidence,
        image_path,
        advice
    ]
    
    # Load existing events
    events = get_events()
    events.append(event)
    
    # Save back to file
    with open(STORAGE_FILE, "w") as f:
        json.dump(events, f, indent=2)
    
    print(f"Logged event: {pest} at {datetime.fromtimestamp(timestamp)}")

def get_events(limit=50):
    """Get recent events"""
    if not os.path.exists(STORAGE_FILE):
        return []
    
    try:
        with open(STORAGE_FILE, "r") as f:
            events = json.load(f)
        # Return most recent first, limited to 'limit'
        return events[-limit:][::-1]
    except (json.JSONDecodeError, IOError):
        return []
