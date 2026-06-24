"""Embedding utilities for vector operations."""
from typing import List, Optional
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self):
        self._model = None

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        # If OpenAI is available, use their embeddings
        try:
            from app.core.config import settings
            if settings.OPENAI_API_KEY and not settings.MOCK_MODE:
                return self._openai_embeddings(texts)
        except Exception:
            pass

        # Fallback: simple TF-IDF-like hash embeddings for demo
        return self._tfidf_fallback(texts)

    def _openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        try:
            from openai import OpenAI
            from app.core.config import settings
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-3-small",
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.warning("OpenAI embeddings failed: %s", e)
            return self._tfidf_fallback(texts)

    def _tfidf_fallback(self, texts: List[str]) -> List[List[float]]:
        """Simple TF-IDF fallback for demo mode."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=128)
            tfidf_matrix = vectorizer.fit_transform(texts)
            return tfidf_matrix.toarray().tolist()
        except Exception:
            # Ultimate fallback: random but deterministic embeddings
            import hashlib
            import numpy as np
            embeddings = []
            for text in texts:
                hash_val = hashlib.sha256(text.encode()).hexdigest()
                seed = int(hash_val[:8], 16)
                rng = np.random.RandomState(seed)
                emb = rng.randn(128).tolist()
                embeddings.append(emb)
            return embeddings


# Singleton
embedding_service = EmbeddingService()
