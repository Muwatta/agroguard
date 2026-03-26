import time

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
    
    # Remove old visits outside window (5 minutes)
    window = 300  # VISIT_WINDOW_SEC
    visits[pest] = [t for t in visits[pest] if now - t < window]
    
    # Return True if persistent (2+ visits in window)
    threshold = 2  # VISIT_THRESHOLD
    return len(visits[pest]) >= threshold