import random
import os

LABELS = ["bird", "armyworm", "beetle", "weevil", "grasshopper"]

def classify(image_path):
    if not os.path.exists(image_path):
        return "unknown", 0.0
    pest = random.choice(LABELS)
    confidence = random.uniform(0.75, 0.95)
    print(f"[DUMMY] Classified {os.path.basename(image_path)}: {pest} ({confidence:.2f})")
    return pest, confidence
