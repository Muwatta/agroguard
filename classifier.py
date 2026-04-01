#!/usr/bin/env python3
"""
AgroGuard AI - Optimized TFLite Classifier for 5 Pest Classes
"""

import os
import json
import numpy as np
import cv2

try:
    from tflite_runtime.interpreter import Interpreter
    print("Using tflite_runtime (optimized for Pi)")
except ImportError:
    try:
        from tensorflow.lite.python.interpreter import Interpreter
        print("Using TensorFlow Lite (development mode)")
    except ImportError:
        Interpreter = None
        print("No TFLite interpreter available; classifier will not run.")

class PestClassifier:
    def __init__(self, model_path='model/pest_model.tflite', confidence_threshold=0.6):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.interpreter = None
        self.input_shape = (224, 224)
        self.class_names = ['armyworm', 'aphid', 'mealybug', 'stem_borer', 'weevil']
        self.floating_model = False
        self.model_output_dim = None
        self._load_model()
    
    def _load_model(self):
        if Interpreter is None:
            print("No TFLite interpreter available; classifier disabled.")
            return

        if not os.path.exists(self.model_path):
            print(f"Model not found at {self.model_path}")
            return

        try:
            self.interpreter = Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.floating_model = self.input_details[0]['dtype'] == np.float32
            self.input_shape = tuple(self.input_details[0]['shape'][1:3])
            self.model_output_dim = self.output_details[0]['shape'][-1]

            if self.model_output_dim != len(self.class_names):
                print(f"Warning: model output dim ({self.model_output_dim}) != class_names len ({len(self.class_names)}).")

            print(f"Model loaded: {self.input_shape}")
            print(f"Model output dim: {self.model_output_dim}")
            print(f"Confidence threshold: {self.confidence_threshold}")
            print(f"Classes: {self.class_names}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.interpreter = None
    
    def preprocess(self, image):
        img = cv2.resize(image, self.input_shape)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if self.floating_model:
            img = img.astype(np.float32) / 255.0
        return np.expand_dims(img, axis=0)
    
    def classify(self, image_path):
        if isinstance(image_path, str):
            image = cv2.imread(image_path)
            if image is None:
                return "unknown", 0.0
        else:
            image = image_path
        
        if self.interpreter is None:
            print("Classifier not initialized.")
            return "unknown", 0.0
        
        input_data = self.preprocess(image)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        if not self.floating_model:
            scale, zero_point = self.output_details[0]['quantization']
            output_data = scale * (output_data - zero_point)
        
        probs = {name: float(output_data[i]) for i, name in enumerate(self.class_names)}
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        
        top_class, top_confidence = sorted_probs[0]
        second_confidence = sorted_probs[1][1] if len(sorted_probs) > 1 else 0
        
        prob_str = ", ".join([f"{n}:{p:.2f}" for n, p in sorted_probs])
        print(f"Probs: {prob_str}")
        
        # Confidence checks
        if top_confidence < self.confidence_threshold:
            return "unidentified", top_confidence
        if top_confidence - second_confidence < 0.25:
            return "unidentified", top_confidence
        if max(probs.values()) - min(probs.values()) < 0.40:
            return "unidentified", top_confidence
        
        print(f"Detected: {top_class} ({top_confidence})")
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