"""Templates de prompt."""

from app.ports.repository import ScoredChunk

NOT_FOUND_ANSWER = "Não encontrei essa informação nos documentos enviados."

_TEMPLATE = """Você é um assistente que responde perguntas sobre documentos educacionais.
Responda sempre em português.

Regras:
1. Use SOMENTE fatos escritos no contexto abaixo. Nunca use conhecimento próprio.
2. Cite as fontes pelo número entre colchetes, por exemplo [1].
3. Perguntas sobre o assunto, o resumo ou o conteúdo do documento são válidas: responda
   com base no contexto.
4. Se a pergunta pedir algo que não é uma informação presente no contexto (receitas,
   instruções, opiniões, hipóteses, textos criativos, "como ele faria", "imagine que"),
   ou se o contexto não contiver a resposta, responda exatamente e apenas: "{not_found}"
5. Mesmo que a pergunta mencione pessoas ou assuntos do contexto, não invente nada que
   não esteja escrito nele.

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
