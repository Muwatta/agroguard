#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import os
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions

class PestClassifier:
    def __init__(self, conf_threshold=0.5):
        self.conf_threshold = conf_threshold
        # Use pre-trained model
        self.model = MobileNetV2(weights='imagenet')
        
        # Map ImageNet classes to pests
        self.pest_mapping = {
            'ant': 'armyworm',
            'bee': 'weevil',
            'beetle': 'weevil',
            'bug': 'aphid',
            'caterpillar': 'armyworm',
            'worm': 'armyworm',
            'fly': 'aphid',
            'locust': 'armyworm'
        }
        
    def classify(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            return 'none', 0.0
        
        # Preprocess for MobileNet
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)
        
        # Predict
        preds = self.model.predict(img, verbose=0)
        results = decode_predictions(preds, top=3)[0]
        
        # Check for insect-related predictions
        for _, label, confidence in results:
            label_lower = label.lower()
            for keyword, pest in self.pest_mapping.items():
                if keyword in label_lower and confidence > self.conf_threshold:
                    return pest, confidence
        
        # Default based on color detection
        hsv = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2HSV)
        
        # Check for green (plants)
        green = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
        green_ratio = np.sum(green > 0) / green.size
        
        if green_ratio > 0.3:
            return 'none', 0.85
        else:
            return 'unidentified', 0.40

def get_classifier():
    global _classifier
    if '_classifier' not in globals():
        _classifier = PestClassifier()
    return _classifier

def classify(image_path):
    classifier = get_classifier()
    return classifier.classify(image_path)
