"""RAG (Retrieval-Augmented Generation) service."""
from typing import Any, Dict, List, Optional
from app.services.provider_router import call_provider_method, get_provider_with_reason
from app.services.document_parser import document_parser
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Maximum chunks passed to the AI when the MOCK provider is active.
# Keeping this small makes mock responses return almost instantly because
# there is no ChromaDB initialisation or embedding overhead. This cap does
# NOT apply when a real provider (gemini/openai/huggingface) is active —
# those get full ChromaDB-retrieved (or all parsed) chunks instead.
_MOCK_MAX_CHUNKS = 5


class RagService:
    """Service for RAG-based document Q&A."""

    def query(
        self,
        file_id: str,
        question: str,
        use_rag: bool = True,
        provider_hint: Optional[str] = None,
        file_content: Optional[bytes] = None,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a RAG query against a document.

        Chunk-retrieval strategy depends on the ACTUAL effective provider for
        this request (resolved via get_provider_with_reason — saved
        settings/runtime state, not the static settings.MOCK_MODE env value).
        Previously this checked settings.MOCK_MODE directly, which meant a
        user who saved mock_mode=False and selected Gemini would still see
        the fast 5-chunk mock path and "skipping ChromaDB" in the logs even
        though Gemini was supposed to be active — this is the fix for that.

        Mock-active path
        -----------------
        When the resolved active provider is mock, skip all ChromaDB/embedding
        work: parse the document, take the first _MOCK_MAX_CHUNKS chunks, and
        pass those straight to MockAIService. Returns in milliseconds.

        Real-provider-active path
        --------------------------
        When a real provider (gemini/openai/huggingface/anthropic) is active,
        use ChromaDB for semantic retrieval (falling back to ALL parsed
        chunks, uncapped, if the vector store is unavailable) before calling
        that provider. If the live call then fails for any reason, the
        result is a request-scoped fallback to mock — see
        provider_router.call_provider_method.
        """
        # Resolve the effective provider for THIS request before deciding the
        # chunk-retrieval strategy. call_provider_method() below resolves it
        # again internally when it actually executes — both calls are pure/
        # cheap given the same runtime state, so this is safe and keeps the
        # two concerns (chunk strategy vs. provider execution) independent.
        active_provider, _ = get_provider_with_reason(provider_hint)

        chunks: List[str] = []

        if use_rag and file_content and filename:
            # ── Step 1: parse the document (always lightweight, always runs
            # regardless of which provider will answer) ──────────────────────
            parsed = document_parser.parse(file_content, filename)
            doc_chunks = parsed.get("chunks", [])
            all_chunk_texts: List[str] = [c["text"] for c in doc_chunks]

            if active_provider == "mock":
                # ── Fast path: no vector store ────────────────────────────────
                chunks = all_chunk_texts[:_MOCK_MAX_CHUNKS]
                logger.debug(
                    "Mock is the active provider: using first %d/%d chunks, skipping ChromaDB",
                    len(chunks),
                    len(all_chunk_texts),
                )
            else:
                # ── Real provider active: use ChromaDB for semantic retrieval ──
                chunks = all_chunk_texts  # fallback if vector store fails: ALL chunks, not capped
                try:
                    from app.vectorstore.chroma_store import chroma_store
                    if file_id and all_chunk_texts:
                        chroma_store.add_document(file_id, all_chunk_texts)
                    # Pass file_id so ChromaDB filters to THIS document only —
                    # prevents answers from a previously uploaded file leaking in.
                    relevant = chroma_store.query(question, n_results=5, doc_id=file_id)
                    if relevant:
                        chunks = [r["text"] for r in relevant]
                except Exception as e:
                    logger.warning(
                        "Vector store unavailable for provider '%s', using all %d parsed chunks: %s",
                        active_provider, len(all_chunk_texts), e,
                    )

        # Deduplicate chunks (same text can appear twice from re-indexing or
        # overlapping retrieval) and cap total context length so the LLM
        # prompt stays within a sensible token budget.
        if chunks:
            seen: set = set()
            deduped: list = []
            for c in chunks:
                key = c.strip()[:200]  # normalise by first 200 chars as key
                if key not in seen:
                    seen.add(key)
                    deduped.append(c)
            chunks = deduped

            MAX_CONTEXT_CHARS = 8000
            total_chars = 0
            capped: list = []
            for c in chunks:
                total_chars += len(c)
                if total_chars > MAX_CONTEXT_CHARS:
                    break
                capped.append(c)
            chunks = capped or chunks[:1]  # always keep at least one chunk

        # ── Safe call: resolves provider, calls with the standardized
        # keyword-only interface, falls back to mock on any failure ──────────
        result, provider = call_provider_method(
            "rag_query",
            provider_hint=provider_hint,
            question=question,
            file_id=file_id,
            chunks=chunks,
            filename=filename,
            use_rag=use_rag,
        )
        result["_effective_provider"] = provider  # consumed by the route, not exposed to frontend
        return result


# Singleton
rag_service = RagService()
