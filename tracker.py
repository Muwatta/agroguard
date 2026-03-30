import time
from config import VISIT_WINDOW_SEC, VISIT_THRESHOLD

# Store visit timestamps
visits = {}

def register_visit(pest):
    """
    Register a pest visit and return True if it's persistent
    """
    now = time.time()
    
    if pest not in visits:
        visits[pest] = []
    
    # Add current timestamp
    visits[pest].append(now)
    
    # Remove old visits outside window
    window = VISIT_WINDOW_SEC
    visits[pest] = [t for t in visits[pest] if now - t < window]
    
    # Return True if persistent
    threshold = VISIT_THRESHOLD
    return len(visits[pest]) >= threshold