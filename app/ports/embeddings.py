"""Porta para geração de embeddings."""

from abc import ABC, abstractmethod


class EmbeddingsPort(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Devolve um vetor por texto, na mesma ordem."""

    @abstractmethod
    def ping(self) -> None:
        """Levanta exceção se o provedor não estiver disponível."""
