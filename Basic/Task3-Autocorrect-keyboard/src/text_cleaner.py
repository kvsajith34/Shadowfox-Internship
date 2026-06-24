import re


WORD_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
SENTENCE_SPLIT_PATTERN = re.compile(r"[.!?]+")


def normalize_whitespace(text: str) -> str:
    """Collapse repeated spaces and trim outer whitespace."""
    return re.sub(r"\s+", " ", text).strip()


def clean_text(text: str) -> str:
    """Lowercase text and remove symbols except sentence punctuation and apostrophes."""
    lowered = text.lower()
    cleaned = re.sub(r"[^a-z0-9\s.!?'-]", " ", lowered)
    return normalize_whitespace(cleaned)


def tokenize_words(text: str) -> list[str]:
    """Extract word tokens while preserving contractions."""
    return WORD_PATTERN.findall(text.lower())


def split_sentences(text: str) -> list[str]:
    """Split text into sentences for n-gram training."""
    cleaned = clean_text(text)
    parts = [normalize_whitespace(part) for part in SENTENCE_SPLIT_PATTERN.split(cleaned)]
    return [part for part in parts if part]


def get_last_word(text: str) -> str:
    """Return the last alphabetic token from an input string."""
    tokens = WORD_PATTERN.findall(text)
    return tokens[-1] if tokens else ""