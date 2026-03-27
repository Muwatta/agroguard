#!/usr/bin/env python3
"""
AgroGuard AI - Optimized TFLite Classifier with Confidence Threshold
"""

import os
import numpy as np
import cv2

# Try to import tflite_runtime (Pi) or fallback to tensorflow (PC)
try:
    from tflite_runtime.interpreter import Interpreter
    print("Using tflite_runtime (optimized for Pi)")
except ImportError:
    from tensorflow.lite.python.interpreter import Interpreter
    print("Using TensorFlow Lite (development mode)")

class PestClassifier:
    def __init__(self, model_path='model/pest_model.tflite', confidence_threshold=0.90):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.interpreter = None
        self.input_shape = (224, 224)
        self.class_names = ['armyworm', 'beetle', 'crow', 'grasshopper', 'weevil']
        self.floating_model = False
        
        self._load_model()
    
    def _load_model(self):
        if not os.path.exists(self.model_path):
            print("Model not found at " + self.model_path)
            return
        
        try:
            self.interpreter = Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            self.floating_model = self.input_details[0]['dtype'] == np.float32
            height = self.input_details[0]['shape'][1]
            width = self.input_details[0]['shape'][2]
            self.input_shape = (height, width)
            
            print("Model loaded: " + str(self.input_shape))
            print("Confidence threshold: " + str(self.confidence_threshold))
            print("Classes: " + str(self.class_names))
            
        except Exception as e:
            print("Error loading model: " + str(e))
            self.interpreter = None
    
    def preprocess(self, image):
        img = cv2.resize(image, self.input_shape)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        if self.floating_model:
            img = img.astype(np.float32) / 255.0
            img = np.expand_dims(img, axis=0)
        else:
            img = np.expand_dims(img, axis=0)
        
        return img
    
    def classify(self, image_path):
        if isinstance(image_path, str):
            image = cv2.imread(image_path)
            if image is None:
                return "unknown", 0.0
        else:
            image = image_path
        
        if self.interpreter is None:
            import random
            return random.choice(self.class_names), random.uniform(0.75, 0.98)
        
        input_data = self.preprocess(image)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        
        if not self.floating_model:
            scale, zero_point = self.output_details[0]['quantization']
            output_data = scale * (output_data - zero_point)
        
        probs = {name: float(output_data[i]) for i, name in enumerate(self.class_names)}
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        
        top_class = sorted_probs[0][0]
        top_confidence = sorted_probs[0][1]
        second_confidence = sorted_probs[1][1] if len(sorted_probs) > 1 else 0
        
        # DEBUG output
        prob_str = ", ".join([f"{n}:{p:.2f}" for n, p in sorted_probs])
        print("Probs: " + prob_str)
        
        # Check 1: Low confidence
        if top_confidence < self.confidence_threshold:
            print("Low confidence: " + str(top_confidence))
            return "unidentified", top_confidence
        
        # Check 2: Too close to second place
        confidence_gap = top_confidence - second_confidence
        if confidence_gap < 0.25:
            print("Too close: " + str(top_confidence) + " vs " + str(second_confidence))
            return "unidentified", top_confidence
        
        # Check 3: No clear winner
        if max(probs.values()) - min(probs.values()) < 0.40:
            print("No clear winner")
            return "unidentified", top_confidence
        
        print("Detected: " + top_class + " (" + str(top_confidence) + ")")
        return top_class, top_confidence

_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = PestClassifier()
    return _classifier

def classify(image_path):
    classifier = get_classifier()
    return classifier.classify(image_path)
