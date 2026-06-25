<div align="center">

# <img width="35" height="35" alt="image" src="https://github.com/user-attachments/assets/a514850e-c3ad-4309-9bbe-6ac9e78761dc" /> Shadowfox Internship Projects
</div>

This repository contains task-wise projects completed as part of the **Shadowfox Internship**, organized across **Basic**, **Intermediate**, and **Advanced** difficulty levels. The projects cover Python programming, data analysis, machine learning, NLP, computer vision, and a full-stack multimodal AI application.

---

## 📋 Quick Overview

| Level | Task | Project Name | Domain | Status |
|---|---|---|---|---|
| Basic | Task 1 | Image Tagging | Computer Vision / Deep Learning | ✅ Complete |
| Basic | Task 2 | Boston House Price Prediction | Regression / ML | ✅ Complete |
| Basic | Task 3 | Autocorrect Keyboard | NLP / Text Processing | ✅ Complete |
| Intermediate | Task 1 | Store Sales Profit Analysis | Data Analysis / EDA | ✅ Complete |
| Intermediate | Task 2 | Car Price Prediction | Regression / ML | ✅ Complete |
| Intermediate | Task 3 | Loan Approval Prediction | Classification / ML | ✅ Complete |
| Advanced | — | VisualRAG Intelligence Studio | Multimodal AI / Full-Stack | 🟡 Partially Working  |

---

## 🗂 Repository Structure

```
Shadowfox-Internship/
├── Basic/
│   ├── Task1-Image_Tagging/
│   ├── Task2-Boston-house-price-prediction/
│   └── Task3-Autocorrect-keyboard/
├── Intermediate/
│   ├── Task1-Store-sales-profit-analysis/
│   ├── Task2-Car-price-prediction/
│   └── Task-3-Loan_Approval/
└── Advanced/
    └── Visualrag-intelligence-studio/
```

---

## 🟢 Basic Level Projects

### Task 1 — Image Tagging

A machine learning / deep learning based image tagging and classification project. It processes input images and predicts or assigns meaningful labels/tags using a trained model.

**Skills demonstrated:**
- Image preprocessing and loading
- Model-based prediction workflow
- Computer vision fundamentals
- Python project structure

---

### Task 2 — Boston House Price Prediction

A regression-based machine learning project using the classic Boston Housing dataset to predict house prices. Covers the end-to-end ML workflow from data preparation to evaluation.

**Skills demonstrated:**
- Regression modeling (scikit-learn)
- Data preprocessing and feature-target separation
- Train/test split and model evaluation
- Python ML pipeline

---

### Task 3 — Autocorrect Keyboard

An intelligent autocorrect system that detects misspelled words and suggests likely corrections using NLP-style logic and word frequency analysis.

**Skills demonstrated:**
- Text preprocessing
- Word matching and correction logic
- NLP fundamentals (edit distance / probability-based selection)
- Suggestion generation in Python

---

## 🟡 Intermediate Level Projects

### Task 1 — Store Sales Profit Analysis

A data analysis project using a superstore sales dataset to explore business trends across product categories, regions, and customer segments. Produces visual insights from raw sales data.

**Skills demonstrated:**
- Exploratory Data Analysis (EDA)
- Sales and profit trend analysis
- Data cleaning and transformation
- Visualization (matplotlib / seaborn)
- CSV dataset handling

---

### Task 2 — Car Price Prediction

A regression project that predicts the selling price of used cars based on features such as manufacturing year, present price, kilometers driven, fuel type, seller type, transmission, and ownership history.

**Skills demonstrated:**
- Regression modeling
- Categorical feature encoding
- Feature engineering
- Model evaluation metrics
- Predictive analytics workflow

---

### Task 3 — Loan Approval Prediction

A classification project that predicts whether a loan application is likely to be approved based on applicant details including income, education, credit history, loan amount, and property area.

**Skills demonstrated:**
- Binary classification modeling
- Missing-value handling
- Categorical encoding
- ML pipeline structure
- Evaluation metrics (accuracy, precision, recall)

---

## 🔴 Advanced Project

### VisualRAG Intelligence Studio

A full-stack multimodal AI document intelligence application with a **React/Vite** frontend and a **Python FastAPI** backend. It supports document upload, RAG-based PDF chat, visual analysis, invoice extraction, chart interpretation, and an answer evaluation lab.

**Key features:**
- PDF upload and RAG-based question answering
- Document summarization
- Visual chat workflow
- Invoice data extraction
- Chart analysis
- Answer evaluation — relevance, faithfulness, and hallucination risk scoring
- Dashboard and report views
- Multi-provider support: Gemini, OpenAI, Hugging Face, and mock fallback mode
- ChromaDB-based vector retrieval
- FastAPI REST backend with auto-generated API docs

#### ⚠️ Known Limitations / Current Notes

| Area | Status |
|---|---|
| Backend | Runs successfully |
| Frontend | Runs successfully |
| File upload & PDF RAG | Working |
| Gemini (primary provider) | Working — may fall back to mock under quota/rate limits |
| OpenAI | Detected but falls back to mock due to quota/rate-limit errors |
| Hugging Face | May fall back to mock due to model availability or connection issues |
| Anthropic | Not configured — no API key added |
| List-style answers | May trigger DB save warnings when a provider returns a list instead of plain text |

These are active areas of improvement and do not affect the core pipeline functionality.

---

## 🛠 Tech Stack

| Category | Technologies |
|---|---|
| Programming | Python, TypeScript / JavaScript |
| ML / Data | pandas, NumPy, scikit-learn, TensorFlow / Keras, matplotlib, seaborn |
| Backend | FastAPI, Uvicorn |
| Frontend | React, Vite, Tailwind CSS |
| AI / RAG | Gemini API, OpenAI API, Hugging Face, ChromaDB, mock fallback |
| Tools | Git, GitHub, VS Code |

---

## ⚙️ How to Run

### Basic and Intermediate Tasks

```bash
# Clone the repository
git clone https://github.com/kvsajith34/Shadowfox-Internship.git
cd Shadowfox-Internship

# Navigate to the task folder
cd Basic/Task1-Image_Tagging   # (or any other task folder)

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the script or notebook
python main.py
```

> Each task folder may contain its own README with task-specific instructions. Check there first.

---

### Advanced — VisualRAG Intelligence Studio

**Backend:**
```bash
cd Advanced/Visualrag-intelligence-studio/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # Add your API keys to .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd Advanced/Visualrag-intelligence-studio/frontend
npm install
copy .env.example .env
npm run dev
```

**Access URLs:**

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Health Check | http://localhost:8000/api/v1/health |

---

## 🔐 Environment Variables

All API keys must be placed in `backend/.env` only. **Never commit `.env` files to GitHub.**

The `frontend/.env` file should only contain `VITE_API_BASE_URL` if needed.

Use `.env.example` as a reference template:

```env
MOCK_MODE=false
DEFAULT_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
HF_TOKEN=your_huggingface_token_here
```

---

## 📚 Learning Outcomes

Through these projects, the following skills were developed and applied:

- Python fundamentals and project structuring
- Data analysis and exploratory data analysis (EDA)
- ML regression and classification workflows
- NLP and autocorrect logic implementation
- Computer vision and image classification basics
- Full-stack AI application development
- REST API design and integration
- RAG pipeline and document intelligence
- GitHub documentation and repository organization

---

## 🔮 Future Improvements

- Stabilize OpenAI and Hugging Face provider integrations in the advanced project
- Resolve list-style answer saving in the database layer
- Add Anthropic API support with proper key configuration
- Add screenshots and demo videos for all projects
- Improve Hugging Face model configuration and fallback handling
- Add deployment instructions (Docker / cloud hosting)
- Expand evaluation reports in VisualRAG Intelligence Studio

---

## 👤 Author

**Venkata Sai Ajith Kancheti**

GitHub: [@kvsajith34](https://github.com/kvsajith34)

---

*This repository was created as part of the Shadowfox Internship program.*
