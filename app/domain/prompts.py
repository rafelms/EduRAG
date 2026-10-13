"""Templates de prompt."""

from app.ports.repository import ScoredChunk

NOT_FOUND_ANSWER = "Não encontrei essa informação nos documentos enviados."

_TEMPLATE = """Você é um assistente que responde perguntas sobre documentos educacionais.
Responda sempre em português, usando SOMENTE as informações do contexto abaixo.
Cite as fontes pelo número entre colchetes, por exemplo [1].
Se o contexto não contiver a resposta, diga exatamente: "{not_found}"

Contexto:
{context}

Pergunta: {question}

Resposta:"""


def build_qa_prompt(question: str, chunks: list[ScoredChunk]) -> str:
    context = "\n\n".join(
        f"[{i}] ({chunk.filename}, página {chunk.page})\n{chunk.content}"
        for i, chunk in enumerate(chunks, start=1)
    )
    return _TEMPLATE.format(not_found=NOT_FOUND_ANSWER, context=context, question=question)
