"""Fakes para os testes: LLM, embeddings e repositório em memória."""

import hashlib
import math
import re
import uuid
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.ports.embeddings import EmbeddingsPort
from app.ports.llm import LLMPort
from app.ports.repository import (
    DocumentRecord,
    DocumentRepository,
    DocumentStatus,
    NewChunk,
    QuestionRecord,
    ScoredChunk,
)

DIMENSIONS = 768


class FakeEmbeddings(EmbeddingsPort):
    """Embedding determinístico por saco de palavras: textos com palavras em comum ficam
    próximos, textos sem nada em comum ficam ortogonais."""

    def __init__(self) -> None:
        self.calls: list[list[str]] = []  # lotes de documentos
        self.queries: list[str] = []
        self.available = True

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [self._vector(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        self.queries.append(text)
        return self._vector(text)

    def ping(self) -> None:
        if not self.available:
            raise ConnectionError("embeddings fora do ar")

    @staticmethod
    def _vector(text: str) -> list[float]:
        vector = [0.0] * DIMENSIONS
        for word in re.findall(r"\w+", text.lower()):
            index = int(hashlib.md5(word.encode()).hexdigest(), 16) % DIMENSIONS
            vector[index] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class FakeLLM(LLMPort):
    def __init__(self, answer: str = "Resposta de teste [1].") -> None:
        self.answer = answer
        self.prompts: list[str] = []
        self.available = True

    @property
    def model_name(self) -> str:
        return "fake-llm"

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.answer

    def ping(self) -> None:
        if not self.available:
            raise ConnectionError("llm fora do ar")


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


class InMemoryRepository(DocumentRepository):
    def __init__(self) -> None:
        self.documents: dict[UUID, DocumentRecord] = {}
        self.chunks: dict[UUID, list[NewChunk]] = {}
        self.questions: list[QuestionRecord] = []

    def create_document(self, filename: str) -> DocumentRecord:
        record = DocumentRecord(
            id=uuid.uuid4(),
            filename=filename,
            status=DocumentStatus.PROCESSANDO,
            pages=None,
            error=None,
            created_at=datetime.now(UTC),
        )
        self.documents[record.id] = record
        return record

    def get_document(self, document_id: UUID) -> DocumentRecord | None:
        return self.documents.get(document_id)

    def list_documents(self) -> list[DocumentRecord]:
        return sorted(self.documents.values(), key=lambda d: d.created_at, reverse=True)

    def update_status(
        self,
        document_id: UUID,
        status: DocumentStatus,
        pages: int | None = None,
        error: str | None = None,
    ) -> None:
        current = self.documents.get(document_id)
        if current is None:
            return
        self.documents[document_id] = DocumentRecord(
            id=current.id,
            filename=current.filename,
            status=status,
            pages=pages,
            error=error,
            created_at=current.created_at,
        )

    def delete_document(self, document_id: UUID) -> bool:
        self.chunks.pop(document_id, None)
        return self.documents.pop(document_id, None) is not None

    def add_chunks(self, document_id: UUID, chunks: list[NewChunk]) -> None:
        self.chunks.setdefault(document_id, []).extend(chunks)

    def search(
        self, embedding: list[float], top_k: int, document_ids: list[UUID] | None = None
    ) -> list[ScoredChunk]:
        scored = [
            ScoredChunk(
                document_id=doc_id,
                filename=self.documents[doc_id].filename,
                page=chunk.page,
                content=chunk.content,
                score=_cosine(embedding, chunk.embedding),
            )
            for doc_id, chunks in self.chunks.items()
            if self.documents[doc_id].status == DocumentStatus.PRONTO
            and (not document_ids or doc_id in document_ids)
            for chunk in chunks
        ]
        return sorted(scored, key=lambda c: c.score, reverse=True)[:top_k]

    def save_question(
        self,
        question: str,
        answer: str,
        sources: list[dict[str, Any]],
        model: str,
        latency_ms: int,
    ) -> QuestionRecord:
        record = QuestionRecord(
            id=uuid.uuid4(),
            question=question,
            answer=answer,
            sources=sources,
            model=model,
            latency_ms=latency_ms,
            created_at=datetime.now(UTC),
        )
        self.questions.append(record)
        return record

    def list_questions(self, limit: int, offset: int) -> tuple[list[QuestionRecord], int]:
        ordered = sorted(self.questions, key=lambda q: q.created_at, reverse=True)
        return ordered[offset : offset + limit], len(ordered)

    def ping(self) -> None:
        return None
