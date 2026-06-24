"""Document parsing service for PDF, TXT, CSV files."""
import io
import os
from typing import Dict, Any, List, Optional
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class DocumentParser:
    """Parse various document formats into text."""

    def parse(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Parse a file and return extracted text and metadata."""
        ext = os.path.splitext(filename)[1].lower()

        if ext == ".pdf":
            return self.parse_pdf(file_content)
        elif ext in (".txt", ".md"):
            return self.parse_text(file_content)
        elif ext == ".csv":
            return self.parse_csv(file_content)
        else:
            return {
                "text": "",
                "metadata": {"error": f"Unsupported format: {ext}"},
                "chunks": [],
                "page_count": 0,
            }

    def parse_pdf(self, file_content: bytes) -> Dict[str, Any]:
        """Extract text from a PDF file."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_content, filetype="pdf")
            pages = []
            for page in doc:
                pages.append(page.get_text())
            full_text = "\n\n".join(pages)
            doc.close()
            return {
                "text": full_text,
                "metadata": {
                    "page_count": len(pages),
                    "format": "pdf",
                    "char_count": len(full_text),
                },
                "chunks": self._chunk_text(full_text),
                "page_count": len(pages),
            }
        except ImportError:
            # Fallback to pdfplumber
            try:
                import pdfplumber
                pdf = pdfplumber.open(io.BytesIO(file_content))
                pages = []
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    pages.append(text)
                full_text = "\n\n".join(pages)
                pdf.close()
                return {
                    "text": full_text,
                    "metadata": {"page_count": len(pages), "format": "pdf", "char_count": len(full_text)},
                    "chunks": self._chunk_text(full_text),
                    "page_count": len(pages),
                }
            except Exception as e:
                logger.warning("PDF parsing failed: %s", e)
                return {"text": "", "metadata": {"error": str(e)}, "chunks": [], "page_count": 0}
        except Exception as e:
            logger.warning("PDF parsing failed: %s", e)
            return {"text": "", "metadata": {"error": str(e)}, "chunks": [], "page_count": 0}

    def parse_text(self, file_content: bytes) -> Dict[str, Any]:
        """Parse a plain text file."""
        try:
            text = file_content.decode("utf-8", errors="replace")
            return {
                "text": text,
                "metadata": {"format": "text", "char_count": len(text)},
                "chunks": self._chunk_text(text),
                "page_count": 1,
            }
        except Exception as e:
            logger.warning("Text parsing failed: %s", e)
            return {"text": "", "metadata": {"error": str(e)}, "chunks": [], "page_count": 0}

    def parse_csv(self, file_content: bytes) -> Dict[str, Any]:
        """Parse a CSV file into text representation."""
        try:
            import pandas as pd
            df = pd.read_csv(io.BytesIO(file_content))
            text = df.to_string()
            return {
                "text": text,
                "metadata": {
                    "format": "csv",
                    "rows": len(df),
                    "columns": list(df.columns),
                    "char_count": len(text),
                },
                "chunks": self._chunk_text(text),
                "page_count": 1,
            }
        except Exception as e:
            logger.warning("CSV parsing failed: %s", e)
            return {"text": "", "metadata": {"error": str(e)}, "chunks": [], "page_count": 0}

    def _chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks for RAG."""
        if not text.strip():
            return []

        chunks = []
        words = text.split()
        chunk_words = []
        chunk_index = 0

        for word in words:
            chunk_words.append(word)
            if len(chunk_words) >= chunk_size:
                chunk_text = " ".join(chunk_words)
                chunks.append({
                    "chunk_id": f"chunk_{chunk_index}",
                    "text": chunk_text,
                    "index": chunk_index,
                    "word_count": len(chunk_words),
                })
                chunk_index += 1
                # Keep overlap words
                chunk_words = chunk_words[-overlap:] if overlap > 0 else []

        # Remaining words
        if chunk_words:
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "chunk_id": f"chunk_{chunk_index}",
                "text": chunk_text,
                "index": chunk_index,
                "word_count": len(chunk_words),
            })

        return chunks


# Singleton
document_parser = DocumentParser()
