# Intelligent Autocorrect Keyboard

A Python NLP prototype that combines real-time spell correction with context-aware next-word prediction, served through an interactive Streamlit web interface.

---

## Overview

This project demonstrates a lightweight keyboard intelligence system built with standard NLP techniques. It detects misspelled words as a user types, proposes corrections, rebuilds the corrected sentence, and predicts the most likely next words using an n-gram language model trained on a local corpus.

---

## Features

- **Live spelling feedback** — detects and highlights misspelled words as you type, showing the best correction alongside ranked candidate suggestions
- **Sentence autocorrection** — rewrites the full input with corrections applied while preserving the original punctuation and casing
- **Next-word prediction** — uses a trigram model with bigram and unigram backoff to suggest the most probable following words
- **Configurable sidebar** — toggle autocorrect and prediction on or off, and adjust the number of next-word suggestions returned
- **Modular architecture** — spell correction, n-gram modelling, text cleaning, and the orchestration layer are each isolated in their own module

---

## Tech Stack

| Layer | Library |
|---|---|
| UI | Streamlit |
| Spell correction | pyspellchecker |
| Language model | Custom n-gram (trigram / bigram / unigram backoff) |
| Text processing | Python `re` (regex) |
| Testing | pytest |
| Python | 3.10+ |

---

## Project Structure

```
intelligent-autocorrect-keyboard/
│
├── app.py                    # Streamlit entry point
├── requirements.txt
├── README.md
├── run_project.md
│
├── data/
│   └── sample_corpus.txt     # Training corpus for the n-gram model
│
├── src/
│   ├── __init__.py
│   ├── text_cleaner.py       # Tokenization, normalization, sentence splitting
│   ├── spell_corrector.py    # Misspelling detection and correction via pyspellchecker
│   ├── ngram_model.py        # Trigram model with bigram/unigram backoff
│   └── keyboard_engine.py    # Orchestrates spell correction + prediction pipeline
│
├── tests/
│   ├── test_spell_corrector.py
│   └── test_ngram_model.py
│
└── outputs/
    └── sample_results.md     # Example inputs and outputs
```

---

## How It Works

1. The user types text into the Streamlit input area.
2. `text_cleaner.py` normalizes whitespace and tokenizes the input, preserving contractions and sentence boundaries.
3. `spell_corrector.py` identifies unknown tokens using `pyspellchecker` and maps each to its best correction and ranked candidates.
4. The corrected sentence is reconstructed via regex substitution, preserving original formatting.
5. `ngram_model.py` reads the corrected context and returns the top-*k* next-word predictions using trigram counts, backing off to bigram then unigram if the context is unseen.
6. `keyboard_engine.py` ties both components together and returns a single structured result to the UI.

---

## Getting Started

**1. Clone or extract the project**

```bash
cd intelligent-autocorrect-keyboard
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the app**

```bash
streamlit run app.py
```

**5. Run the tests**

```bash
pytest tests/
```

---

## Example

**Input**
```
I am goinng to the markket
```

**Output**

| Field | Value |
|---|---|
| Misspelled words | `goinng → going`, `markket → market` |
| Corrected sentence | `I am going to the market` |
| Next-word predictions | `market, school, office, store, city` |

---

## Notes

This is a basic prototype intended as a foundation for further development. The n-gram model is trained on the bundled `sample_corpus.txt`; replacing this file with a larger domain-specific corpus will improve prediction quality.

**Possible future directions:**

- Personal dictionary support for custom vocabulary
- Edit-distance ranking for smarter correction ordering
- User-adaptive prediction based on typing history
- REST API layer for mobile keyboard integration
- Export of analysis results to CSV or JSON

---

## Author

**KVS Ajith** — AI/ML and NLP
