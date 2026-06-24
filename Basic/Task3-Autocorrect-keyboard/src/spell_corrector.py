import re

from spellchecker import SpellChecker

from .text_cleaner import WORD_PATTERN, tokenize_words


class SpellCorrector:
    """Spell correction helper built on top of pyspellchecker."""

    def __init__(self) -> None:
        self.spell = SpellChecker()

    def find_misspelled_words(self, text: str) -> dict[str, str]:
        tokens = tokenize_words(text)
        unknown_words = self.spell.unknown(tokens)
        misspelled_map: dict[str, str] = {}

        for word in tokens:
            lower_word = word.lower()
            if lower_word in unknown_words and lower_word not in misspelled_map:
                misspelled_map[lower_word] = self.correct_word(lower_word)

        return misspelled_map

    def get_suggestions(self, word: str, limit: int = 5) -> list[str]:
        lower_word = word.lower()
        candidates = self.spell.candidates(lower_word)
        if not candidates:
            return []

        best = self.spell.correction(lower_word)
        ordered: list[str] = []

        if best:
            ordered.append(best)

        for candidate in sorted(candidates):
            if candidate not in ordered:
                ordered.append(candidate)

        return ordered[:limit]

    def correct_word(self, word: str) -> str:
        lower_word = word.lower()
        corrected = self.spell.correction(lower_word)

        if not corrected:
            return word

        if word.isupper():
            return corrected.upper()
        if word.istitle():
            return corrected.capitalize()
        return corrected

    def correct_sentence(self, text: str) -> str:
        if not text.strip():
            return text

        tokens = tokenize_words(text)
        unknown_words = self.spell.unknown(tokens)

        def replace_word(match: re.Match[str]) -> str:
            token = match.group(0)
            if token.lower() in unknown_words:
                return self.correct_word(token)
            return token

        return WORD_PATTERN.sub(replace_word, text)