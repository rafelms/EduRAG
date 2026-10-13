"""Configuração da aplicação: tudo vem de variáveis de ambiente."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    database_url: str = "postgresql+psycopg://edurag:change-me@localhost:5432/edurag"
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:3b"
    embedding_model: str = "nomic-embed-text"
    llm_timeout_seconds: float = 300.0

    # Limiar mínimo de similaridade (cosseno) para chamar o LLM.
    min_score: float = 0.5
    max_upload_mb: int = 20

    # Tamanho dos trechos, em palavras (aproximação de tokens).
    chunk_size: int = 800
    chunk_overlap: int = 100
    embedding_batch_size: int = 16

    log_level: str = "INFO"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
