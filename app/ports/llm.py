"""Porta para o modelo de linguagem."""

from abc import ABC, abstractmethod


class LLMPort(ABC):
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Nome do modelo, gravado no histórico de perguntas."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Gera uma resposta em texto para o prompt."""

    @abstractmethod
    def ping(self) -> None:
        """Levanta exceção se o provedor não estiver disponível."""
