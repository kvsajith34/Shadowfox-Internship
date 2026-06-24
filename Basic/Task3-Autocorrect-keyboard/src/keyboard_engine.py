from pathlib import Path

from .ngram_model import NGramModel
from .spell_corrector import SpellCorrector


class KeyboardEngine:
    """Combines spell correction and next-word prediction."""

    def __init__(self, corpus_path: str | None = None) -> None:
        self.spell_corrector = SpellCorrector()

        if corpus_path is None:
            project_root = Path(__file__).resolve().parents[1]
            corpus_path = str(project_root / "data" / "sample_corpus.txt")

        self.ngram_model = NGramModel(corpus_path=corpus_path)

    def analyze_text(
        self,
        text: str,
        top_k: int = 5,
        enable_autocorrect: bool = True,
        enable_prediction: bool = True,
    ) -> dict[str, object]:
        original_text = text
        stripped_text = text.strip()

        if not stripped_text:
            return {
                "original_text": original_text,
                "misspelled_words": {},
                "correction_suggestions": {},
                "corrected_text": original_text,
                "next_word_predictions": [],
            }

        misspelled_words: dict[str, str] = {}
        correction_suggestions: dict[str, list[str]] = {}

        if enable_autocorrect:
            misspelled_words = self.spell_corrector.find_misspelled_words(text)
            for word in misspelled_words:
                correction_suggestions[word] = self.spell_corrector.get_suggestions(word)
            corrected_text = self.spell_corrector.correct_sentence(text)
        else:
            corrected_text = text

        prediction_context = corrected_text if enable_autocorrect else text
        if enable_prediction:
            next_word_predictions = self.ngram_model.predict_next_words(prediction_context, top_k=top_k)
        else:
            next_word_predictions = []

        return {
            "original_text": original_text,
            "misspelled_words": misspelled_words,
            "correction_suggestions": correction_suggestions,
            "corrected_text": corrected_text,
            "next_word_predictions": next_word_predictions,
        }