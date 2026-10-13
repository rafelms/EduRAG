"""Serviço de ingestão: PDF -> texto por página -> trechos -> embeddings -> banco."""

import logging
from io import BytesIO
from uuid import UUID

from pypdf import PdfReader

from app.domain.chunking import chunk_pages
from app.ports.embeddings import EmbeddingsPort
from app.ports.repository import DocumentRepository, DocumentStatus, NewChunk

logger = logging.getLogger(__name__)


class EmptyDocumentError(Exception):
    pass


def extract_pages(data: bytes) -> list[str]:
    """Texto de cada página, na ordem. Páginas sem texto viram string vazia."""
    reader = PdfReader(BytesIO(data))
    return [(page.extract_text() or "").strip() for page in reader.pages]


class IngestionService:
    def __init__(
        self,
        repository: DocumentRepository,
        embeddings: EmbeddingsPort,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        batch_size: int = 16,
    ) -> None:
        self._repository = repository
        self._embeddings = embeddings
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._batch_size = batch_size

    def ingest(self, document_id: UUID, data: bytes) -> None:
        """Processa o PDF. Nunca levanta: falhas viram status `erro` com o motivo."""
        try:
            pages = extract_pages(data)
            chunks = chunk_pages(pages, self._chunk_size, self._chunk_overlap)
            if not chunks:
                raise EmptyDocumentError("O PDF não contém texto extraível.")

            vectors = self._embed_all([c.content for c in chunks])
            self._repository.add_chunks(
                document_id,
                [NewChunk(c.page, c.content, v) for c, v in zip(chunks, vectors, strict=True)],
            )
            self._repository.update_status(document_id, DocumentStatus.PRONTO, pages=len(pages))
            logger.info(
                "documento ingerido",
                extra={"document_id": str(document_id), "pages": len(pages), "chunks": len(chunks)},
            )
        except EmptyDocumentError as exc:
            self._fail(document_id, str(exc))
        except Exception as exc:
            logger.exception("falha na ingestão", extra={"document_id": str(document_id)})
            self._fail(document_id, f"Falha ao processar o documento: {type(exc).__name__}")

    def _embed_all(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            vectors.extend(self._embeddings.embed(texts[start : start + self._batch_size]))
        return vectors

    def _fail(self, document_id: UUID, reason: str) -> None:
        self._repository.update_status(document_id, DocumentStatus.ERRO, error=reason)
