import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# Paths
data_dir = 'data/pest_images'
img_height, img_width = 128, 128
batch_size = 32
epochs = 15

# Data augmentation and loading
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    zoom_range=0.2,
    validation_split=0.2
)

train_ds = train_datagen.flow_from_directory(
    data_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_ds = train_datagen.flow_from_directory(
    data_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

# Get class names
class_names = list(train_ds.class_indices.keys())
print(f"\n📋 Classes: {class_names}")
print(f"📊 Training samples: {train_ds.samples}")
print(f"📊 Validation samples: {val_ds.samples}")

# Build model
model = models.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape=(img_height, img_width, 3)),
    layers.MaxPooling2D(2,2),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    layers.Flatten(),
    layers.Dropout(0.5),
    layers.Dense(128, activation='relu'),
    layers.Dense(6, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

# Train
print("\n🚀 Training started...")
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=epochs,
    verbose=1
)

# Save model
model.save('pest_classifier.h5')
print("\n✅ Model saved as pest_classifier.h5")

# Save class names
import json
with open('class_names.json', 'w') as f:
    json.dump(class_names, f)
print("✅ Class names saved as class_names.json")

# Final accuracy
final_acc = history.history['accuracy'][-1]
final_val_acc = history.history['val_accuracy'][-1]
print(f"\n📈 Final Training Accuracy: {final_acc:.2%}")
print(f"📈 Final Validation Accuracy: {final_val_acc:.2%}")
