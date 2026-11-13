"""Configuração da aplicação: tudo vem de variáveis de ambiente."""

from functools import lru_cache
from typing import Literal, Self

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Únicos modelos do Claude que o EduRAG aceita chamar. O modelo é um campo da
# requisição que o nosso código monta: nem o cliente da API nem a resposta do LLM
# (um prompt injection num PDF, por exemplo) conseguem trocá-lo.
ALLOWED_CLAUDE_MODELS = frozenset({"claude-sonnet-5"})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    database_url: str = "postgresql+psycopg://edurag:change-me@localhost:5432/edurag"
    ollama_base_url: str = "http://localhost:11434"
    # Quem gera as respostas. Os embeddings continuam sempre no Ollama.
    llm_provider: Literal["ollama", "claude"] = "ollama"
    llm_model: str = "qwen2.5:3b"
    # SecretStr: não aparece em repr nem em log por acidente.
    anthropic_api_key: SecretStr | None = None
    # Teto de saída por resposta do Claude.
    llm_max_tokens: int = 1024
    embedding_model: str = "nomic-embed-text"
    # Prefixos do nomic-embed-text; deixe vazio para modelos que não usam.
    embedding_document_prefix: str = "search_document: "
    embedding_query_prefix: str = "search_query: "
    llm_timeout_seconds: float = 300.0
    # Janela de contexto enviada ao Ollama; o padrão dele (~4k tokens) corta o prompt.
    llm_num_ctx: int = 8192

    # Limiar mínimo de similaridade (cosseno) para chamar o LLM.
    min_score: float = 0.3
    max_upload_mb: int = 20

    # Tamanho dos trechos, em palavras (aproximação de tokens).
    chunk_size: int = 800
    chunk_overlap: int = 100
    embedding_batch_size: int = 16

    log_level: str = "INFO"

    @model_validator(mode="after")
    def _claude_so_com_modelo_permitido(self) -> Self:
        """Falha ao subir, em vez de chamar um modelo fora da lista."""
        if self.llm_provider != "claude":
            return self
        if self.llm_model not in ALLOWED_CLAUDE_MODELS:
            allowed = ", ".join(sorted(ALLOWED_CLAUDE_MODELS))
            raise ValueError(
                f"LLM_MODEL={self.llm_model!r} não é permitido com LLM_PROVIDER=claude "
                f"(permitidos: {allowed})"
            )
        if self.anthropic_api_key is None or not self.anthropic_api_key.get_secret_value():
            raise ValueError("LLM_PROVIDER=claude exige ANTHROPIC_API_KEY")
        return self

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
