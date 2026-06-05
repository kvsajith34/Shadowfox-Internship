"""
streamlit_app.py
----------------
Simple web app to upload an image and get the predicted class.

Run from project root:
    streamlit run app/streamlit_app.py
"""

import os
import sys
import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image

# Make project root importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
import config

st.set_page_config(page_title="Image Tagging with TensorFlow", page_icon="🖼️", layout="centered")


@st.cache_resource
def load_trained_model():
    """Load the saved model once and cache it."""
    if not os.path.exists(config.MODEL_PATH):
        return None
    return tf.keras.models.load_model(config.MODEL_PATH)


def preprocess(pil_image):
    """Resize + normalize uploaded image for the model."""
    img = pil_image.convert("RGB").resize((config.IMG_WIDTH, config.IMG_HEIGHT))
    arr = np.array(img).astype("float32") / 255.0
    return np.expand_dims(arr, axis=0)


# ---------------- UI ----------------
st.title("🖼️ Image Tagging with TensorFlow")
st.write(
    "Upload an image and the CNN model will predict its category. "
    "Trained on **CIFAR-10**: airplane, automobile (car), bird, cat, deer, "
    "dog, frog, horse, ship, truck."
)

model = load_trained_model()

if model is None:
    st.error(
        "❌ No trained model found.\n\n"
        "Please train the model first by running:\n\n"
        "`python src/train.py`"
    )
    st.stop()

uploaded = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

topk = st.slider("Number of top predictions to show", 1, 5, 3)

if uploaded is not None:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("🔍 Predict"):
        with st.spinner("Predicting..."):
            batch = preprocess(image)
            probs = model.predict(batch, verbose=0)[0]

        top_idx = probs.argsort()[-topk:][::-1]
        best_class = config.CLASS_NAMES[top_idx[0]]
        best_conf = probs[top_idx[0]] * 100

        st.success(f"### Predicted Tag: **{best_class.upper()}** ({best_conf:.2f}%)")

        st.write("#### Top Predictions")
        for i in top_idx:
            cls = config.CLASS_NAMES[i]
            conf = float(probs[i])
            st.write(f"**{cls}** — {conf*100:.2f}%")
            st.progress(min(conf, 1.0))

st.markdown("---")
st.caption("Note: Best results on CIFAR-10 style objects. Real-world photos may vary.")