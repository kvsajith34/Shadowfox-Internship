from pathlib import Path

import streamlit as st

from src.keyboard_engine import KeyboardEngine
from src.text_cleaner import get_last_word


PROJECT_ROOT = Path(__file__).resolve().parent
CORPUS_PATH = PROJECT_ROOT / "data" / "sample_corpus.txt"


@st.cache_resource
def load_engine() -> KeyboardEngine:
    return KeyboardEngine(corpus_path=str(CORPUS_PATH))


def render_misspelled_words(misspelled_words: dict[str, str]) -> None:
    if not misspelled_words:
        st.success("No misspelled words found.")
        return

    for wrong, correct in misspelled_words.items():
        st.write(f"- **{wrong}** -> **{correct}**")


def render_correction_suggestions(correction_suggestions: dict[str, list[str]]) -> None:
    if not correction_suggestions:
        st.info("No correction suggestions available.")
        return

    for word, suggestions in correction_suggestions.items():
        suggestion_line = ", ".join(suggestions) if suggestions else "No suggestions"
        st.write(f"- **{word}**: {suggestion_line}")


def main() -> None:
    st.set_page_config(page_title="Intelligent Autocorrect Keyboard", page_icon="KB", layout="wide")
    st.title("Intelligent Autocorrect Keyboard System")
    st.write(
        "Type text to detect misspellings, generate autocorrections, and predict likely next words using an "
        "n-gram language model."
    )

    with st.sidebar:
        st.header("Settings")
        top_k = st.slider("Number of next-word suggestions", min_value=1, max_value=10, value=5)
        enable_autocorrect = st.checkbox("Enable autocorrect", value=True)
        enable_prediction = st.checkbox("Enable next-word prediction", value=True)

    user_input = st.text_area(
        "Text Input",
        placeholder="Example: I am goinng to the markket",
        height=170,
    )

    engine = load_engine()

    st.subheader("Live Typing Insight")
    last_word = get_last_word(user_input)
    if last_word:
        quick_suggestions = engine.spell_corrector.get_suggestions(last_word)
        st.write(f"Current/last word: **{last_word}**")
        st.write(
            "Spelling suggestions: "
            + (", ".join(quick_suggestions) if quick_suggestions else "No suggestions")
        )
    else:
        st.caption("Start typing to see the current word and quick spelling suggestions.")

    analyze_clicked = st.button("Analyze Text", type="primary")

    if analyze_clicked:
        if not user_input.strip():
            st.warning("Please enter text before analysis.")
            return

        result = engine.analyze_text(
            user_input,
            top_k=top_k,
            enable_autocorrect=enable_autocorrect,
            enable_prediction=enable_prediction,
        )

        st.subheader("Section 1: Misspelled Words")
        render_misspelled_words(result["misspelled_words"])

        st.subheader("Section 2: Correction Suggestions")
        render_correction_suggestions(result["correction_suggestions"])

        st.subheader("Section 3: Corrected Sentence")
        st.write(f"**Original:** {result['original_text']}")
        st.write(f"**Corrected:** {result['corrected_text']}")

        st.subheader("Section 4: Next Word Predictions")
        if result["next_word_predictions"]:
            st.write(", ".join(result["next_word_predictions"]))
        else:
            st.info("No predictions available for the given context.")

    st.subheader("Section 5: How It Works")
    st.markdown(
        "1. Text is cleaned and tokenized while preserving useful punctuation.\n"
        "2. Misspelled words are detected using `pyspellchecker`.\n"
        "3. The sentence is auto-corrected word by word.\n"
        "4. A trigram language model predicts the next word from the corrected context.\n"
        "5. If trigram context is missing, the model falls back to bigram, then unigram."
    )


if __name__ == "__main__":
    main()