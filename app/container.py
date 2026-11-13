"""Montagem das dependências (composition root)."""

from dataclasses import dataclass

from app.adapters.claude_llm import ClaudeLLM
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


def build_llm(settings: Settings) -> LLMPort:
    if settings.llm_provider == "claude":
        # A config já garantiu modelo permitido e chave presente.
        assert settings.anthropic_api_key is not None
        return ClaudeLLM(
            settings.anthropic_api_key.get_secret_value(),
            settings.llm_model,
            timeout=settings.llm_timeout_seconds,
            max_tokens=settings.llm_max_tokens,
            effort=settings.llm_effort,
        )
    return OllamaLLM(
        settings.ollama_base_url,
        settings.llm_model,
        settings.llm_timeout_seconds,
        num_ctx=settings.llm_num_ctx,
    )


def build_services(settings: Settings) -> Services:
    """Serviços de produção: PostgreSQL, embeddings no Ollama e o LLM escolhido."""
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
        llm=build_llm(settings),
    )
