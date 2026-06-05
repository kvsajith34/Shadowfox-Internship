# 🖼️ Image Tagging with TensorFlow

> A custom CNN trained on CIFAR-10 that classifies images into 10 categories — complete with a CLI predictor and an interactive Streamlit web app.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16.1-orange?logo=tensorflow&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red?logo=streamlit&logoColor=white)
![Accuracy](https://img.shields.io/badge/Test%20Accuracy-82.73%25-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Demo](#-demo)
- [Model Architecture](#-model-architecture)
- [Performance](#-performance)
- [Project Structure](#-project-structure)
- [Quickstart](#-quickstart)
- [Usage](#-usage)
- [Configuration & Hyperparameters](#-configuration--hyperparameters)
- [Tech Stack](#-tech-stack)

---

## 🔍 Overview

This project implements an end-to-end **image classification pipeline** using a custom Convolutional Neural Network (CNN) built with TensorFlow/Keras. The model is trained on the **CIFAR-10** benchmark dataset and can tag images into one of 10 real-world object categories.

**Supported classes:**

| ✈️ Airplane | 🚗 Automobile | 🐦 Bird | 🐱 Cat | 🦌 Deer |
|:-----------:|:-------------:|:-------:|:------:|:-------:|
| **🐶 Dog** | **🐸 Frog** | **🐴 Horse** | **🚢 Ship** | **🚚 Truck** |

**Key highlights:**
- Custom 3-block CNN with Batch Normalization and Dropout regularisation
- Built-in Keras data augmentation (flip, rotation, zoom, translation, contrast)
- Efficient `tf.data` input pipeline with shuffle, batch, and prefetch
- Smart training callbacks: EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
- CLI predictor for single-image inference with configurable Top-K output
- Streamlit web UI for browser-based predictions — no coding required
- Fully centralised `config.py` for all hyperparameter tuning

---

## 🎬 Demo

**CLI Prediction:**
```bash
python src/predict.py --image sample_images/dog.jpg --topk 3
```
```
==================================================
 IMAGE TAGGING — PREDICTION
==================================================

Image: sample_images/dog.jpg
Predicted Tag: DOG  (78.43%)

Top-3 predictions:
  1. dog           78.43%
  2. cat           12.11%
  3. deer           5.22%
```

**Web App:**
```bash
streamlit run app/streamlit_app.py
```
Upload any image in your browser → get instant predictions with confidence progress bars.

---

## 🧠 Model Architecture

The model uses a **3-block CNN** architecture designed to be lightweight enough for CPU training while achieving strong accuracy on CIFAR-10's 32×32 images.

```
Input (32×32×3)
    │
    ▼
Data Augmentation ─── RandomFlip · RandomRotation · RandomZoom
    │                  RandomTranslation · RandomContrast
    ▼
┌─────────────────────────────────┐
│  Block 1  │ Conv2D(32) → BN     │
│           │ Conv2D(32) → BN     │
│           │ MaxPool(2×2)        │
│           │ Dropout(0.20)       │
└─────────────────────────────────┘
    │
┌─────────────────────────────────┐
│  Block 2  │ Conv2D(64) → BN     │
│           │ Conv2D(64) → BN     │
│           │ MaxPool(2×2)        │
│           │ Dropout(0.24)       │
└─────────────────────────────────┘
    │
┌─────────────────────────────────┐
│  Block 3  │ Conv2D(128) → BN    │
│           │ Conv2D(128) → BN    │
│           │ MaxPool(2×2)        │
│           │ Dropout(0.28)       │
└─────────────────────────────────┘
    │
    ▼
GlobalAveragePooling2D
    │
Dense(128, relu) → BN → Dropout(0.4)
    │
    ▼
Output: Dense(10, softmax)
```

**Training Callbacks:**

| Callback | Monitor | Config |
|---|---|---|
| `EarlyStopping` | `val_loss` | Patience = 12, restores best weights |
| `ModelCheckpoint` | `val_accuracy` | Saves best model to `models/best_cnn_model.keras` |
| `ReduceLROnPlateau` | `val_loss` | Factor = 0.5, patience = 4, min LR = 1e-6 |

---

## 📊 Performance

Evaluated on the CIFAR-10 test set (10,000 images, unseen during training).

### Overall Metrics

| Metric | Score |
|---|---|
| **Test Accuracy** | **82.73%** |
| Macro Precision | 83.45% |
| Macro Recall | 82.73% |
| Macro F1-Score | 82.56% |

### Per-Class Breakdown

| Class | Precision | Recall | F1-Score |
|---|---|---|---|
| airplane | 86.22% | 87.60% | 86.90% |
| automobile | 89.10% | 94.80% | **91.86%** |
| bird | 82.25% | 73.20% | 77.46% |
| cat | 82.31% | 61.40% | 70.33% |
| deer | 83.07% | 78.00% | 80.45% |
| dog | 82.90% | 70.80% | 76.38% |
| frog | 66.02% | 95.80% | 78.17% |
| horse | 86.08% | 87.20% | 86.64% |
| ship | 92.04% | 87.90% | **89.92%** |
| truck | 84.51% | 90.60% | 87.45% |

> **Best performing:** automobile (F1 91.86%) and ship (F1 89.92%)  
> **Most challenging:** cat (F1 70.33%) and dog (F1 76.38%) — a known difficulty in CIFAR-10 due to visual similarity between the two classes.

---

## 📁 Project Structure

```
image-tagging-tensorflow/
│
├── config.py                   # Central config — all hyperparameters live here
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # CIFAR-10 loading, normalisation, tf.data pipeline
│   ├── model.py                # CNN architecture + augmentation + optimizer factory
│   ├── train.py                # Training script with callbacks
│   ├── evaluate.py             # Metrics, confusion matrix, sample predictions
│   ├── predict.py              # CLI predictor for single images
│   └── utils.py                # Plotting, seeding, report saving, image loading
│
├── app/
│   └── streamlit_app.py        # Streamlit web UI for browser predictions
│
├── models/
│   └── best_cnn_model.keras    # Saved best model (auto-generated by train.py)
│
├── notebooks/
│   └── image_classification_experiment.ipynb   # Exploration notebook
│
├── outputs/
│   ├── plots/
│   │   ├── accuracy_plot.png       # Training vs validation accuracy curve
│   │   ├── loss_plot.png           # Training vs validation loss curve
│   │   ├── confusion_matrix.png    # Heatmap of class-level predictions
│   │   └── sample_predictions.png # Grid of 16 test images (green=correct, red=wrong)
│   └── reports/
│       ├── classification_report.txt   # Full per-class metrics
│       └── confusion_matrix.csv        # Raw confusion matrix data
│
├── sample_images/              # Drop your own images here for CLI prediction
├── requirements.txt
└── .gitignore
```

---

## ⚡ Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/kvsajith34/Shadowfox-Internship.git
cd Basic/Task1-Image_Tagging
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** TensorFlow 2.16.1 requires Python 3.9–3.11. CIFAR-10 (~170 MB) is downloaded automatically by Keras on first run.

---

## 🚀 Usage

All scripts are run from the **project root directory**.

### Train

```bash
python src/train.py
```

Downloads CIFAR-10 (if not cached), trains the CNN, saves the best model to `models/best_cnn_model.keras`, and generates accuracy/loss plots in `outputs/plots/`.

### Evaluate

```bash
python src/evaluate.py
```

Loads the saved model, runs full evaluation on the test set, and saves the classification report, confusion matrix, and a sample prediction grid to `outputs/`.

### Predict (CLI)

```bash
# Basic prediction
python src/predict.py --image sample_images/your_image.jpg

# Show top-5 predictions
python src/predict.py --image sample_images/your_image.jpg --topk 5
```

Supported formats: `.jpg`, `.jpeg`, `.png`

### Web App (Streamlit)

```bash
streamlit run app/streamlit_app.py
```

Opens in your browser at `http://localhost:8501`. Upload an image, choose how many predictions to display, and click **Predict**.

---

## ⚙️ Configuration & Hyperparameters

All tunable settings are centralised in **`config.py`** — no need to edit any other file.

```python
# Training
BATCH_SIZE   = 64       # Try 32 for lower RAM usage
EPOCHS       = 60       # EarlyStopping typically halts earlier
LEARNING_RATE = 0.001   # Adam default; try 0.0005 or 0.0001
DROPOUT_RATE = 0.4      # 0.3–0.5 recommended
BASE_FILTERS = 32       # Filters in the first conv block (32 or 64)
OPTIMIZER    = "adam"   # "adam", "sgd", or "rmsprop"

# Callbacks
EARLY_STOPPING_PATIENCE = 12
REDUCE_LR_PATIENCE      = 4
REDUCE_LR_FACTOR        = 0.5
MIN_LR                  = 1e-6

# Reproducibility
RANDOM_SEED  = 42
```

**Recommended experiments:**

| Goal | Change |
|---|---|
| Faster convergence | Lower `LEARNING_RATE` → `0.0005` |
| Reduce overfitting | Increase `DROPOUT_RATE` → `0.5` |
| More capacity | Set `BASE_FILTERS` → `64` |
| Low-memory machine | Set `BATCH_SIZE` → `32` |

---

## 🛠️ Tech Stack

| Category | Library | Version |
|---|---|---|
| Deep Learning | TensorFlow / Keras | 2.16.1 |
| Numerical Computing | NumPy | ≥ 1.26 |
| Scientific Computing | SciPy | ≥ 1.11 |
| Evaluation Metrics | scikit-learn | ≥ 1.3 |
| Data Handling | pandas | ≥ 2.0 |
| Visualisation | Matplotlib | ≥ 3.7 |
| Visualisation | Seaborn | ≥ 0.12 |
| Image I/O | Pillow | ≥ 10.0 |
| Web Interface | Streamlit | ≥ 1.30 |

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute with attribution.

---

<div align="center">

Built using TensorFlow · CIFAR-10 · Streamlit

</div>