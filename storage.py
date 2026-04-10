import json
import os
from datetime import datetime

# Use logs folder for events
EVENTS_FILE = "logs/events.json"

def ensure_logs_dir():
    """Ensure logs directory exists"""
    os.makedirs(os.path.dirname(EVENTS_FILE), exist_ok=True)

def log_event(timestamp, pest, confidence, image_path, advice):
    """Log a pest detection event"""
    ensure_logs_dir()
    
    event = {
        "timestamp": timestamp,
        "datetime": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        "pest": pest,
        "confidence": float(confidence),
        "image": image_path,
        "advice": advice
    }
    
    try:
        # Load existing events
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, 'r') as f:
                events = json.load(f)
        else:
            events = []
        
        # Add new event
        events.insert(0, event)  # Add to beginning (most recent first)
        
        # Keep only last 1000 events
        events = events[:1000]
        
        # Save back
        with open(EVENTS_FILE, 'w') as f:
            json.dump(events, f, indent=2)
            
        print(f"Logged event: {pest} at {event['datetime']}")
        
    except Exception as e:
        print(f"Error logging event: {e}")

def get_events(limit=None):
    """Get all events"""
    ensure_logs_dir()
    
    try:
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, 'r') as f:
                events = json.load(f)
                if limit:
                    return events[:limit]
                return events
        return []
    except Exception as e:
        print(f"Error reading events: {e}")
        return []

def clear_events():
    """Clear all events (for testing)"""
    ensure_logs_dir()
    
    try:
        if os.path.exists(EVENTS_FILE):
            os.remove(EVENTS_FILE)
            print("All events cleared")
    except Exception as e:
        print(f"Error clearing events: {e}")
