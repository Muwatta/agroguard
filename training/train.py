import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def train():
    IMG_SIZE = 224
    BATCH_SIZE = 16
    
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=0.2,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True
    )
    
    train_gen = train_datagen.flow_from_directory(
        '../dataset_augmented',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )
    
    val_gen = train_datagen.flow_from_directory(
        '../dataset_augmented',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )
    
    # Build model
    base = MobileNetV2(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    base.trainable = False
    
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.5)(x)
    x = Dense(128, activation='relu')(x)

    num_classes = len(train_gen.class_indices)
    print(f"Training on {num_classes} classes: {train_gen.class_indices}")
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base.input, outputs=predictions)
    model.compile(optimizer=Adam(0.001), loss='categorical_crossentropy', metrics=['accuracy'])
    
    # Train
    model.fit(train_gen, validation_data=val_gen, epochs=15, callbacks=[
        EarlyStopping(patience=5, restore_best_weights=True),
        ModelCheckpoint('best_model.h5', save_best_only=True)
    ])
    
    # Save
    model.save('agroguard_pest_model.h5')

    # Persist class mapping for inference pipeline
    import json
    class_names = [None] * num_classes
    for name, idx in train_gen.class_indices.items():
        class_names[idx] = name
    os.makedirs('../model', exist_ok=True)
    with open('../model/class_names.json', 'w') as f:
        json.dump(class_names, f, indent=2)
    print(f"Saved class names to ../model/class_names.json: {class_names}")
    
    # Convert to TFLite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    with open('../model/pest_model.tflite', 'wb') as f:
        f.write(tflite_model)
    
    print("Model saved to ../model/pest_model.tflite")

if __name__ == '__main__':
    train()