"""Serviço de perguntas e respostas."""

import logging
import time
from dataclasses import asdict, dataclass
from uuid import UUID

from app.domain.prompts import NOT_FOUND_ANSWER, build_qa_prompt
from app.ports.embeddings import EmbeddingsPort
from app.ports.llm import LLMPort
from app.ports.repository import DocumentRepository, ScoredChunk

logger = logging.getLogger(__name__)

EXCERPT_CHARS = 300
NO_MODEL = "nenhum"


@dataclass(frozen=True)
class Source:
    document_id: str
    filename: str
    page: int
    excerpt: str
    score: float


@dataclass(frozen=True)
class Answer:
    question_id: UUID
    answer: str
    sources: list[Source]


def _is_refusal(answer: str) -> bool:
    """O LLM respondeu só a frase de recusa do prompt (e não uma resposta que a cite)."""
    normalized = answer.strip().strip("\"'").strip().rstrip(".").lower()
    return normalized == NOT_FOUND_ANSWER.rstrip(".").lower()


def _to_source(chunk: ScoredChunk) -> Source:
    excerpt = chunk.content
    if len(excerpt) > EXCERPT_CHARS:
        excerpt = excerpt[:EXCERPT_CHARS].rstrip() + "..."
    return Source(
        document_id=str(chunk.document_id),
        filename=chunk.filename,
        page=chunk.page,
        excerpt=excerpt,
        score=round(chunk.score, 4),
    )


class QAService:
    def __init__(
        self,
        repository: DocumentRepository,
        embeddings: EmbeddingsPort,
        llm: LLMPort,
        min_score: float,
    ) -> None:
        self._repository = repository
        self._embeddings = embeddings
        self._llm = llm
        self._min_score = min_score

    def ask(self, question: str, document_ids: list[UUID] | None = None, top_k: int = 5) -> Answer:
        started = time.perf_counter()

        query_vector = self._embeddings.embed_query(question)
        chunks = self._repository.search(query_vector, top_k, document_ids)

        if not chunks or chunks[0].score < self._min_score:
            # RF06: sem contexto bom o suficiente, não gastamos uma chamada ao LLM.
            answer_text, sources, model = NOT_FOUND_ANSWER, [], NO_MODEL
        else:
            answer_text = self._llm.generate(build_qa_prompt(question, chunks)).strip()
            model = self._llm.model_name
            # O limiar é frouxo (ver spec, RF06): muitas recusas vêm do próprio LLM.
            # Nesse caso as fontes seriam enganosas, pois não sustentam resposta nenhuma.
            sources = [] if _is_refusal(answer_text) else [_to_source(c) for c in chunks]

        latency_ms = int((time.perf_counter() - started) * 1000)
        record = self._repository.save_question(
            question, answer_text, [asdict(s) for s in sources], model, latency_ms
        )
        logger.info(
            "pergunta respondida",
            extra={
                "question_id": str(record.id),
                "latency_ms": latency_ms,
                "sources": len(sources),
            },
        )
        return Answer(question_id=record.id, answer=answer_text, sources=sources)
