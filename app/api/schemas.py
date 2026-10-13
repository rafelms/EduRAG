"""DTOs de entrada e saída."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.ports.repository import DocumentStatus


class DocumentCreated(BaseModel):
    id: UUID
    status: DocumentStatus


class DocumentOut(BaseModel):
    id: UUID
    filename: str
    status: DocumentStatus
    pages: int | None
    error: str | None
    created_at: datetime


class AskRequest(BaseModel):
    question: str
    document_ids: list[UUID] | None = None
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("a pergunta não pode ser vazia")
        if len(value) > 2000:
            raise ValueError("a pergunta pode ter no máximo 2000 caracteres")
        return value


class SourceOut(BaseModel):
    document_id: str
    filename: str
    page: int
    excerpt: str
    score: float


class AskResponse(BaseModel):
    question_id: UUID
    answer: str
    sources: list[SourceOut]


class QuestionOut(BaseModel):
    id: UUID
    question: str
    answer: str
    sources: list[SourceOut]
    model: str
    latency_ms: int
    created_at: datetime


class QuestionsPage(BaseModel):
    items: list[QuestionOut]
    total: int
    limit: int
    offset: int
