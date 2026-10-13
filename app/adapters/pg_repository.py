"""Adaptador PostgreSQL + pgvector para a porta DocumentRepository."""

from typing import Any
from uuid import UUID

from sqlalchemy import delete, func, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Chunk, Document, Question
from app.ports.repository import (
    DocumentRecord,
    DocumentRepository,
    DocumentStatus,
    NewChunk,
    QuestionRecord,
    ScoredChunk,
)


def _to_document(row: Document) -> DocumentRecord:
    return DocumentRecord(
        id=row.id,
        filename=row.filename,
        status=row.status,
        pages=row.pages,
        error=row.error,
        created_at=row.created_at,
    )


def _to_question(row: Question) -> QuestionRecord:
    return QuestionRecord(
        id=row.id,
        question=row.question,
        answer=row.answer,
        sources=row.sources,
        model=row.model,
        latency_ms=row.latency_ms,
        created_at=row.created_at,
    )


class PgDocumentRepository(DocumentRepository):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create_document(self, filename: str) -> DocumentRecord:
        with self._session_factory() as session:
            row = Document(filename=filename, status=DocumentStatus.PROCESSANDO)
            session.add(row)
            session.commit()
            session.refresh(row)
            return _to_document(row)

    def get_document(self, document_id: UUID) -> DocumentRecord | None:
        with self._session_factory() as session:
            row = session.get(Document, document_id)
            return _to_document(row) if row else None

    def list_documents(self) -> list[DocumentRecord]:
        with self._session_factory() as session:
            rows = session.scalars(select(Document).order_by(Document.created_at.desc()))
            return [_to_document(r) for r in rows]

    def update_status(
        self,
        document_id: UUID,
        status: DocumentStatus,
        pages: int | None = None,
        error: str | None = None,
    ) -> None:
        with self._session_factory() as session:
            row = session.get(Document, document_id)
            if row is None:  # documento excluído durante a ingestão
                return
            row.status = status
            row.pages = pages
            row.error = error
            session.commit()

    def delete_document(self, document_id: UUID) -> bool:
        with self._session_factory() as session:
            # Os trechos saem junto pelo ON DELETE CASCADE.
            result = session.execute(delete(Document).where(Document.id == document_id))
            session.commit()
            return result.rowcount > 0

    def add_chunks(self, document_id: UUID, chunks: list[NewChunk]) -> None:
        with self._session_factory() as session:
            session.add_all(
                Chunk(
                    document_id=document_id,
                    page=c.page,
                    content=c.content,
                    embedding=c.embedding,
                )
                for c in chunks
            )
            session.commit()

    def search(
        self, embedding: list[float], top_k: int, document_ids: list[UUID] | None = None
    ) -> list[ScoredChunk]:
        distance = Chunk.embedding.cosine_distance(embedding)
        stmt = (
            select(Chunk, Document.filename, distance.label("distance"))
            .join(Document, Document.id == Chunk.document_id)
            .where(Document.status == DocumentStatus.PRONTO)
            .order_by(distance)
            .limit(top_k)
        )
        if document_ids:
            stmt = stmt.where(Chunk.document_id.in_(document_ids))
        with self._session_factory() as session:
            return [
                ScoredChunk(
                    document_id=chunk.document_id,
                    filename=filename,
                    page=chunk.page,
                    content=chunk.content,
                    score=1.0 - float(dist),
                )
                for chunk, filename, dist in session.execute(stmt)
            ]

    def save_question(
        self,
        question: str,
        answer: str,
        sources: list[dict[str, Any]],
        model: str,
        latency_ms: int,
    ) -> QuestionRecord:
        with self._session_factory() as session:
            row = Question(
                question=question,
                answer=answer,
                sources=sources,
                model=model,
                latency_ms=latency_ms,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return _to_question(row)

    def list_questions(self, limit: int, offset: int) -> tuple[list[QuestionRecord], int]:
        with self._session_factory() as session:
            total = session.scalar(select(func.count()).select_from(Question)) or 0
            rows = session.scalars(
                select(Question).order_by(Question.created_at.desc()).limit(limit).offset(offset)
            )
            return [_to_question(r) for r in rows], total

    def ping(self) -> None:
        with self._session_factory() as session:
            session.execute(text("SELECT 1"))
