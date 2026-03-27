import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Retrain with 6 classes (5 pests + none)
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)

train_gen = train_datagen.flow_from_directory(
    'dataset_augmented',  # Now has 6 folders
    target_size=(224, 224),
    batch_size=16,
    class_mode='categorical',
    subset='training'
)

val_gen = train_datagen.flow_from_directory(
    'dataset_augmented',
    target_size=(224, 224),
    batch_size=16,
    class_mode='categorical',
    subset='validation'
)

# Build model with 6 outputs
base = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base.trainable = False

x = base.output
x = GlobalAveragePooling2D()(x)
x = Dropout(0.5)(x)
x = Dense(128, activation='relu')(x)
predictions = Dense(6, activation='softmax')(x)  # 6 classes now

model = Model(inputs=base.input, outputs=predictions)
model.compile(optimizer=Adam(0.001), loss='categorical_crossentropy', metrics=['accuracy'])

# Train for just 5-10 epochs (quick)
model.fit(train_gen, validation_data=val_gen, epochs=5, callbacks=[
    EarlyStopping(patience=3, restore_best_weights=True)
])

# Save
model.save('training/best_model_with_none.h5')

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open('model/pest_model.tflite', 'wb') as f:
    f.write(tflite_model)

print("✅ Retrained with 'none' class!")