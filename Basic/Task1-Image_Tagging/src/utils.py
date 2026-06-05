"""
utils.py
--------
Helper functions: plotting, seeding, saving reports, image loading.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Safe backend for saving plots without a display
import matplotlib.pyplot as plt
import tensorflow as tf
from PIL import Image

# Allow "import config" when running scripts from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def set_seeds(seed=config.RANDOM_SEED):
    """Set random seeds for reproducible results."""
    np.random.seed(seed)
    tf.random.set_seed(seed)


def plot_training_history(history, save_dir=config.PLOTS_DIR):
    """
    Plot and save training/validation accuracy and loss curves.
    `history` is the object returned by model.fit().
    """
    os.makedirs(save_dir, exist_ok=True)
    hist = history.history

    # ---- Accuracy plot ----
    plt.figure(figsize=(8, 5))
    plt.plot(hist["accuracy"], label="Train Accuracy")
    plt.plot(hist["val_accuracy"], label="Validation Accuracy")
    plt.title("Training vs Validation Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid(True, alpha=0.3)
    acc_path = os.path.join(save_dir, "accuracy_plot.png")
    plt.savefig(acc_path, dpi=120, bbox_inches="tight")
    plt.close()

    # ---- Loss plot ----
    plt.figure(figsize=(8, 5))
    plt.plot(hist["loss"], label="Train Loss")
    plt.plot(hist["val_loss"], label="Validation Loss")
    plt.title("Training vs Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    loss_path = os.path.join(save_dir, "loss_plot.png")
    plt.savefig(loss_path, dpi=120, bbox_inches="tight")
    plt.close()

    print(f"[utils] Saved accuracy plot -> {acc_path}")
    print(f"[utils] Saved loss plot     -> {loss_path}")


def plot_confusion_matrix(cm, class_names, save_path):
    """Plot and save a confusion matrix heatmap."""
    import seaborn as sns
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names)
    plt.title("Confusion Matrix")
    plt.ylabel("Actual Label")
    plt.xlabel("Predicted Label")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(save_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"[utils] Saved confusion matrix -> {save_path}")


def plot_sample_predictions(images, true_labels, pred_labels, class_names,
                            save_path, num=16):
    """
    Show a grid of sample images with actual vs predicted labels.
    Green title = correct, Red title = wrong.
    """
    num = min(num, len(images))
    cols = 4
    rows = int(np.ceil(num / cols))
    plt.figure(figsize=(12, 3 * rows))
    for i in range(num):
        plt.subplot(rows, cols, i + 1)
        plt.imshow(images[i])
        plt.axis("off")
        actual = class_names[int(true_labels[i])]
        predicted = class_names[int(pred_labels[i])]
        color = "green" if actual == predicted else "red"
        plt.title(f"A: {actual}\nP: {predicted}", color=color, fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"[utils] Saved sample predictions -> {save_path}")


def save_text_report(text, save_path):
    """Save any text content (e.g., classification report) to a file."""
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[utils] Saved report -> {save_path}")


def load_and_preprocess_image(image_path, img_size=(config.IMG_HEIGHT, config.IMG_WIDTH)):
    """
    Load a single external image, resize it, normalize, and add batch dim.
    Returns (batch_array, display_image_array).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = Image.open(image_path).convert("RGB")
    img_resized = img.resize(img_size)
    arr = np.array(img_resized).astype("float32") / 255.0   # normalize 0-1
    batch = np.expand_dims(arr, axis=0)                     # (1, H, W, 3)
    return batch, np.array(img_resized)