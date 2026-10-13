"""Adaptador Ollama para a porta LLMPort."""

import httpx

from app.ports.llm import LLMPort


class OllamaLLM(LLMPort):
    def __init__(self, base_url: str, model: str, timeout: float = 300.0) -> None:
        self._model = model
        # Em CPU a geração é lenta, por isso o timeout generoso.
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, prompt: str) -> str:
        response = self._client.post(
            "/api/generate",
            json={
                "model": self._model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1},
            },
        )
        response.raise_for_status()
        return str(response.json()["response"])

    def ping(self) -> None:
        self._client.get("/api/tags", timeout=3.0).raise_for_status()
