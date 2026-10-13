"""Porta de persistência e os tipos de dados que ela troca com o domínio."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class DocumentStatus(StrEnum):
    PROCESSANDO = "processando"
    PRONTO = "pronto"
    ERRO = "erro"


@dataclass(frozen=True)
class DocumentRecord:
    id: UUID
    filename: str
    status: DocumentStatus
    pages: int | None
    error: str | None
    created_at: datetime


@dataclass(frozen=True)
class NewChunk:
    page: int
    content: str
    embedding: list[float]


@dataclass(frozen=True)
class ScoredChunk:
    document_id: UUID
    filename: str
    page: int
    content: str
    score: float  # similaridade de cosseno: 1 = idêntico


@dataclass(frozen=True)
class QuestionRecord:
    id: UUID
    question: str
    answer: str
    sources: list[dict[str, Any]]
    model: str
    latency_ms: int
    created_at: datetime


class DocumentRepository(ABC):
    @abstractmethod
    def create_document(self, filename: str) -> DocumentRecord:
        """Cria um documento com status `processando`."""

    @abstractmethod
    def get_document(self, document_id: UUID) -> DocumentRecord | None: ...

    @abstractmethod
    def list_documents(self) -> list[DocumentRecord]: ...

    @abstractmethod
    def update_status(
        self,
        document_id: UUID,
        status: DocumentStatus,
        pages: int | None = None,
        error: str | None = None,
    ) -> None: ...

    @abstractmethod
    def delete_document(self, document_id: UUID) -> bool:
        """Remove o documento e seus trechos. False se não existir."""

    @abstractmethod
    def add_chunks(self, document_id: UUID, chunks: list[NewChunk]) -> None: ...

    @abstractmethod
    def search(
        self, embedding: list[float], top_k: int, document_ids: list[UUID] | None = None
    ) -> list[ScoredChunk]:
        """Trechos mais próximos, do maior para o menor score."""

    @abstractmethod
    def save_question(
        self,
        question: str,
        answer: str,
        sources: list[dict[str, Any]],
        model: str,
        latency_ms: int,
    ) -> QuestionRecord: ...

    @abstractmethod
    def list_questions(self, limit: int, offset: int) -> tuple[list[QuestionRecord], int]:
        """Página do histórico (mais recentes primeiro) e o total."""

    @abstractmethod
    def ping(self) -> None:
        """Levanta exceção se o banco não responder."""
