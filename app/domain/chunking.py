"""Divisão do texto em trechos com sobreposição, preservando a página."""

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    page: int  # começa em 1
    content: str


def chunk_pages(pages: list[str], size: int = 800, overlap: int = 100) -> list[TextChunk]:
    """Divide cada página em janelas de `size` palavras com `overlap` de sobreposição.

    Palavras são uma aproximação de tokens. Um trecho nunca cruza a página, para
    que a citação da fonte seja sempre exata. Páginas vazias são ignoradas.
    """
    if size <= 0:
        raise ValueError("size deve ser positivo")
    if not 0 <= overlap < size:
        raise ValueError("overlap deve estar entre 0 e size - 1")

    chunks: list[TextChunk] = []
    for page_number, text in enumerate(pages, start=1):
        chunks.extend(_split_page(page_number, text.split(), size, overlap))
    return chunks


def _split_page(page: int, words: list[str], size: int, overlap: int) -> Iterator[TextChunk]:
    if not words:
        return
    step = size - overlap
    start = 0
    while True:
        yield TextChunk(page=page, content=" ".join(words[start : start + size]))
        if start + size >= len(words):
            return
        start += step
