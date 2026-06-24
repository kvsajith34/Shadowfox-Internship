"""ChromaDB vector store for RAG retrieval."""
import os
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ChromaStore:
    """ChromaDB-based vector store for document chunks."""

    def __init__(self):
        self._client = None
        self._collection = None

    def _get_client(self):
        """Lazy-initialize ChromaDB client."""
        if self._client is None:
            try:
                import chromadb
                os.makedirs(settings.CHROMA_DIR, exist_ok=True)
                self._client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
                self._collection = self._client.get_or_create_collection(
                    name="visualrag_documents",
                    metadata={"hnsw:space": "cosine"},
                )
                logger.info("ChromaDB initialized at %s", settings.CHROMA_DIR)
            except Exception as e:
                logger.warning("ChromaDB init failed: %s", e)
                self._client = None
        return self._client

    def _get_collection(self):
        """Get or create the collection."""
        self._get_client()
        return self._collection

    def add_document(self, doc_id: str, chunks: List[str]) -> bool:
        """Add document chunks to the vector store.

        Deletes any previously indexed chunks for this doc_id before adding
        the new ones. This prevents duplicate chunks from accumulating when
        the same file is re-uploaded or re-indexed (which was causing the
        "same answer repeated" bug: ChromaDB held stale chunks from earlier
        uploads and mixed them with new ones in retrieval results).
        """
        collection = self._get_collection()
        if collection is None:
            logger.warning("ChromaDB unavailable, skipping add_document")
            return False

        try:
            # Remove stale entries for this doc_id first
            self.delete_document(doc_id)

            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            collection.upsert(
                ids=ids,
                documents=chunks,
                metadatas=[{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))],
            )
            logger.info("Added %d chunks for doc %s", len(chunks), doc_id)
            return True
        except Exception as e:
            logger.warning("Failed to add document chunks: %s", e)
            return False

    def query(self, query_text: str, n_results: int = 5, doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query the vector store for relevant chunks.

        Parameters
        ----------
        query_text: The question or query string.
        n_results:  Maximum number of chunks to retrieve.
        doc_id:     When supplied, restricts results to chunks that belong to
                    this document. This prevents answers for file A from
                    appearing when the user later asks about file B — a
                    cross-file contamination bug when multiple files have been
                    indexed into the same ChromaDB collection.
        """
        collection = self._get_collection()
        if collection is None:
            logger.warning("ChromaDB unavailable, returning empty results")
            return []

        try:
            total = collection.count()
            if total == 0:
                return []

            where_filter = {"doc_id": doc_id} if doc_id else None
            query_kwargs: Dict[str, Any] = {
                "query_texts": [query_text],
                "n_results": min(n_results, total),
            }
            if where_filter:
                query_kwargs["where"] = where_filter

            results = collection.query(**query_kwargs)

            if not results or not results.get("documents"):
                return []

            retrieved = []
            for i, doc in enumerate(results["documents"][0]):
                retrieved.append({
                    "text": doc,
                    "id": results["ids"][0][i] if results.get("ids") else f"result_{i}",
                    "similarity": 1.0 - (results["distances"][0][i] if results.get("distances") and results["distances"][0] else 0.0),
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") and results["metadatas"][0] else {},
                })
            return retrieved
        except Exception as e:
            logger.warning("Vector query failed: %s", e)
            return []

    def delete_document(self, doc_id: str) -> bool:
        """Delete all chunks for a document."""
        collection = self._get_collection()
        if collection is None:
            return False

        try:
            # Get all chunk IDs for this document
            results = collection.get(where={"doc_id": doc_id})
            if results and results["ids"]:
                collection.delete(ids=results["ids"])
            return True
        except Exception as e:
            logger.warning("Failed to delete document: %s", e)
            return False


# Singleton
chroma_store = ChromaStore()
