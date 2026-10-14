"""Adaptador Ollama para a porta EmbeddingsPort."""

import httpx

from app.ports.embeddings import EmbeddingsPort


class OllamaEmbeddings(EmbeddingsPort):
    def __init__(
        self,
        base_url: str,
        model: str,
        document_prefix: str = "",
        query_prefix: str = "",
        timeout: float = 120.0,
    ) -> None:
        self._model = model
        self._document_prefix = document_prefix
        self._query_prefix = query_prefix
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed([self._document_prefix + t for t in texts])

    def embed_query(self, text: str) -> list[float]:
        [vector] = self._embed([self._query_prefix + text])
        return vector

    def _embed(self, texts: list[str]) -> list[list[float]]:
        response = self._client.post("/api/embed", json={"model": self._model, "input": texts})
        response.raise_for_status()
        embeddings: list[list[float]] = response.json()["embeddings"]
        if len(embeddings) != len(texts):
            raise RuntimeError("O Ollama devolveu um número inesperado de embeddings.")
        return embeddings

    def ping(self) -> None:
        self._client.get("/api/tags", timeout=3.0).raise_for_status()
