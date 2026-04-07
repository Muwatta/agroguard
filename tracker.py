# tracker.py
import time
from collections import defaultdict
from datetime import datetime, timedelta
from config import VISIT_WINDOW_SEC, VISIT_THRESHOLD

# Store visit timestamps for each pest
pest_visits = defaultdict(list)

def register_visit(pest_name):
    """
    Register a pest detection and check if it's persistent enough.
    Returns True if the pest should be alerted, False otherwise.
    """
    current_time = time.time()
    
    # Add current visit
    pest_visits[pest_name].append(current_time)
    
    # Clean old visits outside the time window
    cutoff = current_time - VISIT_WINDOW_SEC
    pest_visits[pest_name] = [t for t in pest_visits[pest_name] if t > cutoff]
    
    # Check if we have enough visits in the window
    visit_count = len(pest_visits[pest_name])
    
    print(f"Pest {pest_name} visit count in last {VISIT_WINDOW_SEC}s: {visit_count}/{VISIT_THRESHOLD}")
    
    return visit_count >= VISIT_THRESHOLD

def clear_visits(pest_name=None):
    """Clear visit history for a specific pest or all pests"""
    if pest_name:
        pest_visits[pest_name] = []
    else:
        pest_visits.clear()

def get_visit_count(pest_name):
    """Get current visit count for a pest"""
    return len(pest_visits[pest_name])