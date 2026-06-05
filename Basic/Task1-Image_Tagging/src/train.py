"""
train.py
--------
Trains the CNN on CIFAR-10 with callbacks and saves the best model.

Run from project root:
    python src/train.py
"""

import os
import sys
import tensorflow as tf
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.data_loader import load_cifar10, make_tf_datasets
from src.model import build_cnn_model, compile_model
from src.utils import set_seeds, plot_training_history


def main():
    print("=" * 60)
    print(" IMAGE TAGGING WITH TENSORFLOW — TRAINING")
    print("=" * 60)

    config.ensure_dirs()
    set_seeds()

    # 1. Load data
    (x_train, y_train), (x_val, y_val), (x_test, y_test), class_names = load_cifar10()

    # 2. Build tf.data pipelines
    train_ds, val_ds = make_tf_datasets(x_train, y_train, x_val, y_val)

    # 3. Build + compile model (with augmentation)
    model = build_cnn_model(include_augmentation=True)
    model = compile_model(model)
    model.summary()

    # 4. Callbacks
    callbacks = [
        EarlyStopping(
            monitor="val_loss",
            patience=config.EARLY_STOPPING_PATIENCE,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=config.MODEL_PATH,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=config.REDUCE_LR_FACTOR,
            patience=config.REDUCE_LR_PATIENCE,
            min_lr=config.MIN_LR,
            verbose=1
        ),
    ]

    # 5. Train
    print("\n[train] Starting training... (this may take a while on CPU)\n")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=config.EPOCHS,
        callbacks=callbacks,
        verbose=1
    )

    # 6. Plots
    plot_training_history(history)

    # 7. Quick test-set check
    print("\n[train] Evaluating best model on the test set...")
    best_model = tf.keras.models.load_model(config.MODEL_PATH)
    test_loss, test_acc = best_model.evaluate(x_test, y_test, verbose=0)
    print(f"[train] Test Accuracy: {test_acc:.4f} | Test Loss: {test_loss:.4f}")

    print(f"\n[train] Best model saved to: {config.MODEL_PATH}")
    print("[train] Done! Run evaluate.py next for full metrics.\n")


if __name__ == "__main__":
    main()