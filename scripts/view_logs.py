#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import sys
from datetime import datetime
from collections import Counter

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Path to events file
EVENTS_FILE = "logs/events.json"

def view_recent(limit=10):
    """View recent detections"""
    if not os.path.exists(EVENTS_FILE):
        print("No events logged yet")
        return
    
    with open(EVENTS_FILE, 'r') as f:
        events = json.load(f)
    
    if not events:
        print("No events found")
        return
    
    print("\n" + "="*70)
    print(f"RECENT PEST DETECTIONS (Last {min(limit, len(events))} of {len(events)} total)")
    print("="*70 + "\n")
    
    for i, event in enumerate(events[:limit]):
        date = datetime.fromtimestamp(event['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        confidence_pct = event['confidence'] * 100
        print(f"{i+1}. [{date}]")
        print(f"   Pest: {event['pest'].upper()} ({confidence_pct:.1f}% confidence)")
        print(f"   Image: {event['image']}")
        print(f"   Advice: {event['advice'][:80]}...")
        print()

def show_stats():
    """Show statistics"""
    if not os.path.exists(EVENTS_FILE):
        print("No events logged yet")
        return
    
    with open(EVENTS_FILE, 'r') as f:
        events = json.load(f)
    
    if not events:
        print("No events found")
        return
    
    # Count by pest
    pest_counts = Counter(e['pest'] for e in events)
    
    # Average confidence
    avg_confidence = sum(e['confidence'] for e in events) / len(events) * 100
    
    # Time range
    timestamps = [e['timestamp'] for e in events]
    first_detection = datetime.fromtimestamp(min(timestamps))
    last_detection = datetime.fromtimestamp(max(timestamps))
    
    print("\n" + "="*70)
    print("DETECTION STATISTICS")
    print("="*70)
    print(f"\nSummary:")
    print(f"   Total detections: {len(events)}")
    print(f"   Average confidence: {avg_confidence:.1f}%")
    print(f"   First detection: {first_detection}")
    print(f"   Last detection: {last_detection}")
    days = (last_detection - first_detection).days
    print(f"   Detection period: {days} days")
    
    print(f"\nPest Breakdown:")
    for pest, count in pest_counts.most_common():
        print(f"   {pest}: {count} detection(s)")

def clear_logs():
    """Clear all logs (with confirmation)"""
    confirm = input("Are you sure you want to delete all logs? (yes/no): ")
    if confirm.lower() == 'yes':
        if os.path.exists(EVENTS_FILE):
            os.remove(EVENTS_FILE)
            print("All logs cleared")
            # Recreate empty events file
            with open(EVENTS_FILE, 'w') as f:
                json.dump([], f)
        else:
            print("No logs to clear")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "stats":
            show_stats()
        elif command == "clear":
            clear_logs()
        elif command.isdigit():
            view_recent(int(command))
        else:
            print("Usage: python view_logs.py [number|stats|clear]")
            print("  number: Show recent N detections (e.g., python view_logs.py 5)")
            print("  stats: Show statistics")
            print("  clear: Clear all logs")
    else:
        view_recent(10)
