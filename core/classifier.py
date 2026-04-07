"""
Pest classifier using trained Keras model (pest_classifier.h5)
"""

import cv2
import numpy as np
import json
import os
from tensorflow.keras.models import load_model

class PestClassifier:
    def __init__(self, model_path='pest_classifier.h5', class_path='class_names.json', conf_threshold=0.5):
        self.conf_threshold = conf_threshold
        self.model = None
        self.class_names = []
        self.load_model(model_path, class_path)
    
    def load_model(self, model_path, class_path):
        try:
            if not os.path.exists(model_path):
                print(f"⚠️ Model file not found: {model_path}")
                return
            if not os.path.exists(class_path):
                print(f"⚠️ Class file not found: {class_path}")
                return
            
            self.model = load_model(model_path)
            with open(class_path, 'r') as f:
                self.class_names = json.load(f)
            print(f"✅ Loaded Keras model with {len(self.class_names)} classes: {self.class_names}")
        except Exception as e:
            print(f"❌ Failed to load AI model: {e}")
            self.model = None
    
    def classify(self, image_path):
        """Return (class_name, confidence)"""
        if self.model is None:
            # Fallback: simple detection
            img = cv2.imread(image_path)
            if img is None:
                return 'none', 0.0
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_percent = np.sum(edges > 0) / edges.size
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
            green_percent = np.sum(green_mask > 0) / green_mask.size
            if green_percent > 0.4:
                return 'none', 0.85
            elif edge_percent > 0.05:
                return 'armyworm', 0.75
            else:
                return 'none', 0.90
        
        try:
            img = cv2.imread(image_path)
            if img is None:
                return 'none', 0.0
            
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (128, 128))
            img = img.astype('float32') / 255.0
            img = np.expand_dims(img, axis=0)
            
            preds = self.model.predict(img, verbose=0)[0]
            idx = np.argmax(preds)
            confidence = float(preds[idx])
            class_name = self.class_names[idx]
            return class_name, confidence
        except Exception as e:
            print(f"Prediction error: {e}")
            return 'none', 0.0

# Singleton
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = PestClassifier()
    return _classifier

def classify(image_path):
    return get_classifier().classify(image_path)