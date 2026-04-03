#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
import tensorflow as tf
import os
import json

class PestClassifier:
    def __init__(self, model_path="model/pest_model.tflite", conf_threshold=0.6):
        self.conf_threshold = conf_threshold
        
        # Load TFLite model
        try:
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.is_tflite = True
            print(f"✅ Model loaded: {model_path}")
        except Exception as e:
            print(f"❌ Model load error: {e}")
            self.is_tflite = False
        
        # Load class names
        class_file = model_path.replace('.tflite', '_classes.json')
        if os.path.exists(class_file):
            with open(class_file, 'r') as f:
                self.class_names = json.load(f)
        else:
            self.class_names = ['aphid', 'armyworm', 'mealybugs', 'none', 'stem_borers', 'weevil']
        
        print(f"Classes: {self.class_names}")
    
    def preprocess_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            return None
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        return img
    
    def classify(self, image_path):
        img = self.preprocess_image(image_path)
        if img is None:
            return 'none', 0.0
        
        if self.is_tflite and self.interpreter:
            self.interpreter.set_tensor(self.input_details[0]['index'], img)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self.output_details[0]['index'])
            probs = output[0]
        else:
            return 'unidentified', 0.0
        
        class_idx = np.argmax(probs)
        confidence = probs[class_idx]
        predicted_class = self.class_names[class_idx] if class_idx < len(self.class_names) else 'none'
        
        if confidence < self.conf_threshold:
            return 'unidentified', confidence
        
        return predicted_class, confidence

def get_classifier():
    global _classifier
    if '_classifier' not in globals():
        _classifier = PestClassifier()
    return _classifier

def classify(image_path):
    classifier = get_classifier()
    return classifier.classify(image_path)
