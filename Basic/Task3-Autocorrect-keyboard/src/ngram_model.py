from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from .text_cleaner import split_sentences, tokenize_words


class NGramModel:
    """Simple backoff n-gram model: trigram -> bigram -> unigram."""

    def __init__(self, corpus_path: str | None = None) -> None:
        self.unigram_counts: Counter[str] = Counter()
        self.bigram_counts: dict[tuple[str], Counter[str]] = defaultdict(Counter)
        self.trigram_counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)

        if corpus_path:
            self.load_corpus(corpus_path)

    def load_corpus(self, corpus_path: str) -> None:
        path = Path(corpus_path)
        if not path.exists():
            raise FileNotFoundError(f"Corpus file not found: {corpus_path}")

        self.train(path.read_text(encoding="utf-8"))

    def train(self, corpus_text: str) -> None:
        self.unigram_counts.clear()
        self.bigram_counts.clear()
        self.trigram_counts.clear()

        sentences = split_sentences(corpus_text)

        for sentence in sentences:
            tokens = tokenize_words(sentence)
            if not tokens:
                continue

            self.unigram_counts.update(tokens)

            for i in range(1, len(tokens)):
                prev_word = (tokens[i - 1],)
                current = tokens[i]
                self.bigram_counts[prev_word][current] += 1

            for i in range(2, len(tokens)):
                prev_words = (tokens[i - 2], tokens[i - 1])
                current = tokens[i]
                self.trigram_counts[prev_words][current] += 1

    def _top_from_counter(self, counter: Counter[str], top_k: int) -> list[str]:
        return [word for word, _ in counter.most_common(top_k)]

    def predict_next_words(self, context: str, top_k: int = 5) -> list[str]:
        if top_k <= 0:
            return []

        context_tokens = tokenize_words(context)
        predictions: list[str] = []

        if len(context_tokens) >= 2:
            tri_key = (context_tokens[-2], context_tokens[-1])
            tri_predictions = self._top_from_counter(self.trigram_counts.get(tri_key, Counter()), top_k)
            predictions.extend(tri_predictions)

        if len(predictions) < top_k and len(context_tokens) >= 1:
            bi_key = (context_tokens[-1],)
            bi_predictions = self._top_from_counter(self.bigram_counts.get(bi_key, Counter()), top_k)
            for word in bi_predictions:
                if word not in predictions:
                    predictions.append(word)

        if len(predictions) < top_k:
            for word, _ in self.unigram_counts.most_common(top_k):
                if word not in predictions:
                    predictions.append(word)
                if len(predictions) == top_k:
                    break

        return predictions[:top_k]