import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
import os
import json

class PestClassifier:
    def __init__(self, model_path="model/pest_model.tflite", class_names=None, conf_threshold=0.75):
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        
        # Try to load TFLite model
        try:
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            
            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            self.input_shape = self.input_details[0]['shape']
            self.is_tflite = True
            print(f"✅ TFLite model loaded: {self.input_shape[1]}x{self.input_shape[2]}")
            
        except Exception as e:
            print(f"⚠️ TFLite model not found, trying Keras model...")
            try:
                self.model = keras.models.load_model(model_path.replace('.tflite', '.h5'))
                self.is_tflite = False
                print(f"✅ Keras model loaded")
            except:
                self.interpreter = None
                self.model = None
                print(f"❌ No model found at {model_path}")
        
        # Load class names
        if class_names:
            self.class_names = class_names
        else:
            # Try to load from file
            class_file = model_path.replace('.tflite', '_classes.json')
            if os.path.exists(class_file):
                with open(class_file, 'r') as f:
                    self.class_names = json.load(f)
                print(f"📋 Loaded {len(self.class_names)} classes from file")
            else:
                # Default classes - note: none should be included if retrained
                self.class_names = ['armyworm', 'aphid', 'mealybugs', 'stem_borers', 'weevil']
                
                # Check if none class exists in dataset
                if os.path.exists("dataset_new/none") or os.path.exists("dataset_augmented/none"):
                    print("⚠️ 'none' class detected but not in model - consider retraining")
        
        # Check if 'none' class is already in class names
        if 'none' not in self.class_names:
            self.class_names.append('none')
            print(f"➕ Added 'none' class to classifier")
        
        self.model_output_dim = len(self.class_names)
        print(f"📊 Model output dimension: {self.model_output_dim}")
        print(f"📋 Classes: {self.class_names}")
    
    def preprocess_image(self, image_path):
        """Preprocess image for inference"""
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize to model input size
        if self.is_tflite and self.interpreter:
            target_size = (self.input_shape[1], self.input_shape[2])
        else:
            target_size = (224, 224)
        
        img = cv2.resize(img, target_size)
        
        # Normalize
        img = img.astype(np.float32) / 255.0
        
        # Add batch dimension
        img = np.expand_dims(img, axis=0)
        
        return img
    
    def classify(self, image_path):
        """Classify pest in image with improved confidence handling"""
        img = self.preprocess_image(image_path)
        if img is None:
            return 'none', 0.0
        
        try:
            if self.is_tflite and self.interpreter:
                # TFLite inference
                self.interpreter.set_tensor(self.input_details[0]['index'], img)
                self.interpreter.invoke()
                output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
                probs = output_data[0]
            elif self.model:
                # Keras inference
                probs = self.model.predict(img, verbose=0)[0]
            else:
                return 'none', 0.0
            
            # Get top predictions
            top_indices = np.argsort(probs)[-3:][::-1]  # Top 3 predictions
            top_class_idx = top_indices[0]
            top_confidence = probs[top_class_idx]
            second_confidence = probs[top_indices[1]] if len(top_indices) > 1 else 0
            
            # Get class names
            if top_class_idx < len(self.class_names):
                predicted_class = self.class_names[top_class_idx]
            else:
                predicted_class = 'none'
            
            # Enhanced confidence checks
            is_none_class = predicted_class == 'none'
            is_low_confidence = top_confidence < self.conf_threshold
            is_ambiguous = (top_confidence - second_confidence) < 0.15  # Small gap between top predictions
            
            # Print probabilities for debugging
            print(f"Probs: ", end="")
            for i, name in enumerate(self.class_names):
                if i < len(probs):
                    print(f"{name}:{probs[i]:.2f}", end=", ")
            print()
            
            # Special handling for 'none' class
            if is_none_class or is_low_confidence or is_ambiguous:
                if is_none_class:
                    print(f"🚫 Classified as 'none' (background/no pest)")
                elif is_low_confidence:
                    print(f"⚠️ Low confidence: {top_confidence:.2f} < {self.conf_threshold}")
                elif is_ambiguous:
                    print(f"⚠️ Ambiguous classification: {predicted_class} vs {self.class_names[top_indices[1]]}")
                return 'unidentified', top_confidence
            
            print(f"🎯 Detected: {predicted_class} ({top_confidence:.4f})")
            return predicted_class, top_confidence
            
        except Exception as e:
            print(f"❌ Classification error: {e}")
            return 'none', 0.0

def get_classifier():
    """Get global classifier instance"""
    global _classifier
    if '_classifier' not in globals():
        _classifier = PestClassifier()
    return _classifier

def classify(image_path):
    """Convenience function for classification"""
    classifier = get_classifier()
    return classifier.classify(image_path)