"""Porta para geração de embeddings."""

from abc import ABC, abstractmethod


class EmbeddingsPort(ABC):
    """Documentos e perguntas têm papéis diferentes: alguns modelos (como o
    nomic-embed-text) esperam um prefixo distinto para cada um."""

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Um vetor por trecho de documento, na mesma ordem."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Vetor de uma pergunta."""

    @abstractmethod
    def ping(self) -> None:
        """Levanta exceção se o provedor não estiver disponível."""
