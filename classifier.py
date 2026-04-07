import cv2
import numpy as np
import json
import os

class PestClassifier:
    def __init__(self, conf_threshold=0.5):
        self.conf_threshold = conf_threshold
        self.class_names = ['aphid', 'armyworm', 'mealybugs', 'none', 'stem_borers', 'weevil']
        print("⚠️ Using fallback detector (no AI model)")
    
    def classify(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            return 'none', 0.0
        
        # Simple edge detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_percent = np.sum(edges > 0) / edges.size
        
        # Simple green detection (plants vs pests)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
        green_percent = np.sum(green_mask > 0) / green_mask.size
        
        # Decision logic
        if green_percent > 0.4:
            return 'none', 0.85
        elif edge_percent > 0.05:
            # Something with edges – treat as pest for demo
            return 'armyworm', 0.75
        else:
            return 'none', 0.90

def get_classifier():
    global _classifier
    if '_classifier' not in globals():
        _classifier = PestClassifier()
    return _classifier

def classify(image_path):
    return get_classifier().classify(image_path)
