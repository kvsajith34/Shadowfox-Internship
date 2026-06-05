"""
predict.py
----------
Predict the class of a single external image from the command line.

Usage (from project root):
    python src/predict.py --image sample_images/test.jpg
    python src/predict.py --image C:\\path\\to\\my_image.png --topk 3
"""

import os
import sys
import argparse
import numpy as np
import tensorflow as tf

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.utils import load_and_preprocess_image


def predict_image(image_path, topk=3):
    """Load model, preprocess image, return top-k predictions."""
    if not os.path.exists(config.MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {config.MODEL_PATH}. Run train.py first."
        )

    model = tf.keras.models.load_model(config.MODEL_PATH)
    batch, _ = load_and_preprocess_image(image_path)
    probs = model.predict(batch, verbose=0)[0]

    topk = min(topk, len(config.CLASS_NAMES))
    top_indices = probs.argsort()[-topk:][::-1]

    results = [(config.CLASS_NAMES[i], float(probs[i])) for i in top_indices]
    return results


def main():
    parser = argparse.ArgumentParser(description="Image Tagging Predictor")
    parser.add_argument("--image", required=True, help="Path to the image file")
    parser.add_argument("--topk", type=int, default=3, help="Number of top predictions")
    args = parser.parse_args()

    print("=" * 50)
    print(" IMAGE TAGGING — PREDICTION")
    print("=" * 50)

    try:
        results = predict_image(args.image, args.topk)
    except Exception as e:
        print(f"[predict] ERROR: {e}")
        return

    best_class, best_conf = results[0]
    print(f"\nImage: {args.image}")
    print(f"Predicted Tag: {best_class.upper()}  ({best_conf*100:.2f}%)\n")

    print(f"Top-{args.topk} predictions:")
    for rank, (cls, conf) in enumerate(results, start=1):
        print(f"  {rank}. {cls:<12} {conf*100:6.2f}%")
    print()


if __name__ == "__main__":
    main()