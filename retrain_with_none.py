# retrain_with_none.py
import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import json

def load_and_preprocess_data(data_dir="dataset_new", img_size=(224, 224)):
    """Load images from dataset_new including none class"""
    print(f"📁 Loading data from {data_dir}...")
    
    images = []
    labels = []
    class_names = []
    
    # Get all class folders
    class_folders = sorted([d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))])
    
    for class_idx, class_name in enumerate(class_folders):
        class_names.append(class_name)
        class_dir = os.path.join(data_dir, class_name)
        
        # Get all images in this class
        image_files = [f for f in os.listdir(class_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
        
        print(f"  📂 {class_name}: {len(image_files)} images")
        
        for img_file in image_files:
            img_path = os.path.join(class_dir, img_file)
            
            # Read and preprocess image
            img = cv2.imread(img_path)
            if img is None:
                continue
            
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize
            img = cv2.resize(img, img_size)
            
            # Normalize
            img = img.astype(np.float32) / 255.0
            
            images.append(img)
            labels.append(class_idx)
    
    print(f"✅ Loaded {len(images)} images from {len(class_names)} classes")
    print(f"📋 Classes: {class_names}")
    
    return np.array(images), np.array(labels), class_names

def create_model(num_classes, input_shape=(224, 224, 3)):
    """Create a simple CNN model for pest classification"""
    model = models.Sequential([
        # Convolutional layers
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.MaxPooling2D(2, 2),
        
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D(2, 2),
        
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D(2, 2),
        
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D(2, 2),
        
        # Flatten and dense layers
        layers.Flatten(),
        layers.Dropout(0.5),
        layers.Dense(512, activation='relu'),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def train_model(images, labels, class_names, epochs=20, batch_size=32):
    """Train the model"""
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        images, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"📊 Training samples: {len(X_train)}")
    print(f"📊 Validation samples: {len(X_val)}")
    
    # Data augmentation for training
    datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        fill_mode='nearest'
    )
    
    # Create model
    model = create_model(len(class_names))
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("\n🔧 Model architecture:")
    model.summary()
    
    # Train model
    print(f"\n🏋️ Training for {epochs} epochs...")
    history = model.fit(
        datagen.flow(X_train, y_train, batch_size=batch_size),
        validation_data=(X_val, y_val),
        epochs=epochs,
        steps_per_epoch=len(X_train) // batch_size,
        verbose=1
    )
    
    # Save model
    model.save('model/pest_model.h5')
    print(f"\n✅ Model saved to model/pest_model.h5")
    
    # Convert to TensorFlow Lite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    
    with open('model/pest_model.tflite', 'wb') as f:
        f.write(tflite_model)
    print(f"✅ TFLite model saved to model/pest_model.tflite")
    
    # Save class names
    with open('model/pest_model_classes.json', 'w') as f:
        json.dump(class_names, f)
    print(f"✅ Class names saved to model/pest_model_classes.json")
    
    # Print final accuracy
    final_accuracy = history.history['accuracy'][-1]
    final_val_accuracy = history.history['val_accuracy'][-1]
    print(f"\n📊 Final training accuracy: {final_accuracy:.4f}")
    print(f"📊 Final validation accuracy: {final_val_accuracy:.4f}")
    
    return model, history

def test_model(model, class_names):
    """Test model on a sample image"""
    print("\n🧪 Testing model on a sample...")
    
    # Try to find a test image
    test_dir = "dataset_new/none"
    test_images = [f for f in os.listdir(test_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    if test_images:
        test_img_path = os.path.join(test_dir, test_images[0])
        img = cv2.imread(test_img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        
        predictions = model.predict(img, verbose=0)[0]
        predicted_class = class_names[np.argmax(predictions)]
        confidence = np.max(predictions)
        
        print(f"  Test image: {test_images[0]}")
        print(f"  Predicted: {predicted_class} ({confidence:.4f})")
        
        # Show top predictions
        top_indices = np.argsort(predictions)[-3:][::-1]
        print("  Top predictions:")
        for idx in top_indices:
            print(f"    {class_names[idx]}: {predictions[idx]:.4f}")

if __name__ == "__main__":
    import tensorflow as tf
    
    print("=" * 60)
    print("AgroGuard - Retraining with None Class")
    print("=" * 60)
    
    # Load data
    images, labels, class_names = load_and_preprocess_data("dataset_new")
    
    if len(images) == 0:
        print("❌ No images found! Please add images to dataset_new/")
        print("Expected structure:")
        print("  dataset_new/")
        print("    armyworm/")
        print("    aphid/")
        print("    mealybug/")
        print("    none/")
        print("    stem_borer/")
        print("    weevil/")
        exit(1)
    
    # Train model
    model, history = train_model(images, labels, class_names, epochs=20)
    
    # Test model
    test_model(model, class_names)
    
    print("\n✅ Retraining complete!")
    print("Now restart your app with: python app.py")