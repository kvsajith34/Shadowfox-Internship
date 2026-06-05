"""
model.py
--------
Defines:
- Data augmentation layers (applied only during training)
- A custom CNN architecture for CIFAR-10
- An optimizer factory
"""

import os
import sys
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def build_augmentation():
    """
    Data augmentation pipeline.
    These layers are ACTIVE only during training (model.fit) and
    automatically disabled during inference/evaluation.
    """
    return models.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.10),       # +/- 10%
        layers.RandomZoom(0.10),           # +/- 10%
        layers.RandomTranslation(0.10, 0.10),
        layers.RandomContrast(0.10),
    ], name="data_augmentation")


def get_optimizer(name=config.OPTIMIZER, lr=config.LEARNING_RATE):
    """Return a Keras optimizer based on config."""
    name = name.lower()
    if name == "adam":
        return optimizers.Adam(learning_rate=lr)
    elif name == "sgd":
        return optimizers.SGD(learning_rate=lr, momentum=0.9)
    elif name == "rmsprop":
        return optimizers.RMSprop(learning_rate=lr)
    else:
        print(f"[model] Unknown optimizer '{name}', defaulting to Adam.")
        return optimizers.Adam(learning_rate=lr)


def build_cnn_model(input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, config.IMG_CHANNELS),
                    num_classes=config.NUM_CLASSES,
                    base_filters=config.BASE_FILTERS,
                    dropout_rate=config.DROPOUT_RATE,
                    include_augmentation=True):
    """
    Build a custom CNN with 3 convolutional blocks.

    Architecture:
      Input -> (Augmentation) ->
      [Conv-Conv-BN-Pool-Dropout] x 3 ->
      GlobalAveragePooling -> Dense -> Dropout -> Output(softmax)

    This is lightweight enough for CPU training while reaching ~80% accuracy.
    """
    f = base_filters

    inputs = layers.Input(shape=input_shape)
    x = inputs

    # Apply augmentation only when building the training model
    if include_augmentation:
        x = build_augmentation()(x)

    # ---- Block 1 ----
    x = layers.Conv2D(f, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(f, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(dropout_rate * 0.5)(x)

    # ---- Block 2 ----
    x = layers.Conv2D(f * 2, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(f * 2, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(dropout_rate * 0.6)(x)

    # ---- Block 3 ----
    x = layers.Conv2D(f * 4, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(f * 4, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(dropout_rate * 0.7)(x)

    # ---- Classifier head ----
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(dropout_rate)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs=inputs, outputs=outputs, name="CIFAR10_CNN")
    return model


def compile_model(model):
    """Compile the model with optimizer, loss, and metrics."""
    model.compile(
        optimizer=get_optimizer(),
        loss="sparse_categorical_crossentropy",  # integer labels
        metrics=["accuracy"]
    )
    return model