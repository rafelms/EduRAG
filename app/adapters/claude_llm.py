"""Adaptador Claude (API da Anthropic) para a porta LLMPort."""

import logging
from typing import Any

import anthropic

from app.config import ALLOWED_CLAUDE_MODELS
from app.domain.prompts import NOT_FOUND_ANSWER
from app.ports.llm import LLMPort, LLMUnavailableError

logger = logging.getLogger(__name__)


class ClaudeLLM(LLMPort):
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: float = 60.0,
        max_tokens: int = 1024,
        client: Any = None,
    ) -> None:
        # A config já valida; repetir aqui protege quem montar o adaptador direto.
        if model not in ALLOWED_CLAUDE_MODELS:
            raise ValueError(f"modelo não permitido: {model!r}")
        self._model = model
        self._max_tokens = max_tokens
        # api_key explícita: sem ela, o SDK cairia em outras credenciais da máquina
        # (perfil do `ant auth login`, por exemplo). max_retries=1 porque o teto de
        # gastos não se resolve repetindo.
        self._client = client or anthropic.Anthropic(
            api_key=api_key, timeout=timeout, max_retries=1
        )

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, prompt: str) -> str:
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                # RAG com contexto fechado: sem raciocínio estendido, que seria cobrado
                # como saída. Sem `fallbacks`: um fallback trocaria de modelo.
                thinking={"type": "disabled"},
                messages=[{"role": "user", "content": prompt}],
            )
        except (anthropic.APIStatusError, anthropic.APIConnectionError) as exc:
            logger.warning("claude indisponível", extra={"error": type(exc).__name__})
            raise LLMUnavailableError(str(exc)) from exc

        usage = response.usage
        logger.info(
            "chamada ao claude",
            extra={
                "model": self._model,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "stop_reason": response.stop_reason,
            },
        )

        if response.stop_reason == "refusal":
            return NOT_FOUND_ANSWER
        return "".join(block.text for block in response.content if block.type == "text")

    def ping(self) -> None:
        # Gratuito: confirma que a chave vale e que o modelo existe para ela.
        try:
            self._client.models.retrieve(self._model, timeout=5.0)
        except (anthropic.APIStatusError, anthropic.APIConnectionError) as exc:
            raise LLMUnavailableError(str(exc)) from exc
