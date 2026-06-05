"""
data_loader.py
--------------
Loads and prepares the CIFAR-10 dataset:
- Loads via Keras
- Normalizes pixel values to [0, 1]
- Splits into train / validation / test
- Prints class names

Also includes an OPTIONAL custom-folder loader using
image_dataset_from_directory (for your own dataset).
"""

import os
import sys
import numpy as np
import tensorflow as tf

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def load_cifar10():
    """
    Load CIFAR-10 from Keras, normalize, and split train/val/test.

    Returns:
        (x_train, y_train), (x_val, y_val), (x_test, y_test), class_names
        - x_* : float32 arrays in [0,1], shape (N, 32, 32, 3)
        - y_* : integer labels shape (N,)
    """
    print("[data_loader] Loading CIFAR-10 from Keras (auto-download if needed)...")
    (x_train_full, y_train_full), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

    # Flatten label arrays from (N,1) -> (N,)
    y_train_full = y_train_full.flatten()
    y_test = y_test.flatten()

    # Normalize pixel values to [0, 1]
    x_train_full = x_train_full.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0

    # Create validation split from training data
    val_size = int(len(x_train_full) * config.VALIDATION_SPLIT)

    # Shuffle indices for a fair split
    rng = np.random.default_rng(config.RANDOM_SEED)
    indices = rng.permutation(len(x_train_full))
    val_idx = indices[:val_size]
    train_idx = indices[val_size:]

    x_val, y_val = x_train_full[val_idx], y_train_full[val_idx]
    x_train, y_train = x_train_full[train_idx], y_train_full[train_idx]

    print(f"[data_loader] Train samples     : {len(x_train)}")
    print(f"[data_loader] Validation samples: {len(x_val)}")
    print(f"[data_loader] Test samples      : {len(x_test)}")
    print(f"[data_loader] Image shape       : {x_train.shape[1:]}")
    print(f"[data_loader] Classes ({config.NUM_CLASSES}): {config.CLASS_NAMES}")

    return (x_train, y_train), (x_val, y_val), (x_test, y_test), config.CLASS_NAMES


def make_tf_datasets(x_train, y_train, x_val, y_val, batch_size=config.BATCH_SIZE):
    """
    Build efficient tf.data pipelines for training and validation.
    (Augmentation is applied INSIDE the model in model.py, only at train time.)
    """
    AUTOTUNE = tf.data.AUTOTUNE

    train_ds = (
        tf.data.Dataset.from_tensor_slices((x_train, y_train))
        .shuffle(buffer_size=10000, seed=config.RANDOM_SEED)
        .batch(batch_size)
        .prefetch(AUTOTUNE)
    )

    val_ds = (
        tf.data.Dataset.from_tensor_slices((x_val, y_val))
        .batch(batch_size)
        .prefetch(AUTOTUNE)
    )

    return train_ds, val_ds


# ---------------------------------------------------------------------
# OPTIONAL: Custom dataset loader (folder-based)
# ---------------------------------------------------------------------
def load_custom_dataset(data_dir, img_size=(config.IMG_HEIGHT, config.IMG_WIDTH),
                        batch_size=config.BATCH_SIZE):
    """
    OPTIONAL — Use this only if you have your own dataset in this structure:

        dataset/
          train/
            class_1/
            class_2/
          test/
            class_1/
            class_2/

    Returns train_ds, val_ds, test_ds, class_names.
    """
    train_dir = os.path.join(data_dir, "train")
    test_dir = os.path.join(data_dir, "test")

    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir, validation_split=config.VALIDATION_SPLIT, subset="training",
        seed=config.RANDOM_SEED, image_size=img_size, batch_size=batch_size
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir, validation_split=config.VALIDATION_SPLIT, subset="validation",
        seed=config.RANDOM_SEED, image_size=img_size, batch_size=batch_size
    )
    test_ds = tf.keras.utils.image_dataset_from_directory(
        test_dir, image_size=img_size, batch_size=batch_size, shuffle=False
    )

    class_names = train_ds.class_names
    print(f"[data_loader] Custom class names: {class_names}")

    # Normalize to [0,1]
    norm = tf.keras.layers.Rescaling(1.0 / 255)
    train_ds = train_ds.map(lambda x, y: (norm(x), y)).prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.map(lambda x, y: (norm(x), y)).prefetch(tf.data.AUTOTUNE)
    test_ds = test_ds.map(lambda x, y: (norm(x), y)).prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds, test_ds, class_names