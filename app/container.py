"""Montagem das dependências (composition root)."""

from dataclasses import dataclass

from app.adapters.ollama_embeddings import OllamaEmbeddings
from app.adapters.ollama_llm import OllamaLLM
from app.adapters.pg_repository import PgDocumentRepository
from app.config import Settings
from app.db.session import create_db_engine, create_session_factory
from app.domain.ingestion import IngestionService
from app.domain.qa import QAService
from app.ports.embeddings import EmbeddingsPort
from app.ports.llm import LLMPort
from app.ports.repository import DocumentRepository


@dataclass
class Services:
    settings: Settings
    repository: DocumentRepository
    embeddings: EmbeddingsPort
    llm: LLMPort
    ingestion: IngestionService
    qa: QAService


def assemble_services(
    settings: Settings,
    repository: DocumentRepository,
    embeddings: EmbeddingsPort,
    llm: LLMPort,
) -> Services:
    return Services(
        settings=settings,
        repository=repository,
        embeddings=embeddings,
        llm=llm,
        ingestion=IngestionService(
            repository,
            embeddings,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            batch_size=settings.embedding_batch_size,
        ),
        qa=QAService(repository, embeddings, llm, min_score=settings.min_score),
    )


def build_services(settings: Settings) -> Services:
    """Serviços de produção: PostgreSQL e Ollama."""
    engine = create_db_engine(settings.database_url)
    return assemble_services(
        settings,
        repository=PgDocumentRepository(create_session_factory(engine)),
        embeddings=OllamaEmbeddings(
            settings.ollama_base_url,
            settings.embedding_model,
            document_prefix=settings.embedding_document_prefix,
            query_prefix=settings.embedding_query_prefix,
        ),
        llm=OllamaLLM(
            settings.ollama_base_url,
            settings.llm_model,
            settings.llm_timeout_seconds,
            num_ctx=settings.llm_num_ctx,
        ),
    )
