from app.domain.prompts import NOT_FOUND_ANSWER
from app.domain.qa import QAService
from app.ports.repository import DocumentStatus, NewChunk
from tests.fakes import FakeEmbeddings, FakeLLM, InMemoryRepository


def setup(min_score: float = 0.3):
    repo = InMemoryRepository()
    embeddings = FakeEmbeddings()
    llm = FakeLLM()
    doc = repo.create_document("edital.pdf")
    texts = {
        3: "as inscricoes estarao abertas ate 15 de outubro",
        7: "a taxa de inscricao custa cem reais",
    }
    vectors = embeddings.embed(list(texts.values()))
    repo.add_chunks(
        doc.id, [NewChunk(p, t, v) for (p, t), v in zip(texts.items(), vectors, strict=True)]
    )
    repo.update_status(doc.id, DocumentStatus.PRONTO, pages=10)
    return repo, llm, QAService(repo, embeddings, llm, min_score=min_score), doc


def test_pergunta_relevante_devolve_resposta_com_fonte_da_pagina_certa():
    repo, llm, qa, doc = setup()

    answer = qa.ask("ate quando vao as inscricoes", top_k=2)

    assert answer.answer == "Resposta de teste [1]."
    assert answer.sources[0].page == 3
    assert answer.sources[0].document_id == str(doc.id)
    assert "[1]" in llm.prompts[0] and "página 3" in llm.prompts[0]


def test_abaixo_do_limiar_nao_chama_o_llm():
    repo, llm, qa, _ = setup(min_score=0.3)

    answer = qa.ask("quem descobriu o brasil")

    assert answer.answer == NOT_FOUND_ANSWER
    assert answer.sources == []
    assert llm.prompts == []


def test_toda_pergunta_e_gravada_no_historico():
    repo, _, qa, _ = setup()

    qa.ask("ate quando vao as inscricoes")
    qa.ask("quem descobriu o brasil")

    answered, not_found = repo.questions
    assert answered.model == "fake-llm" and answered.sources
    assert not_found.model == "nenhum" and not_found.sources == []
    assert answered.latency_ms >= 0


def test_filtro_por_documento_inexistente_nao_encontra():
    from uuid import uuid4

    _, llm, qa, _ = setup()

    answer = qa.ask("ate quando vao as inscricoes", document_ids=[uuid4()])

    assert answer.answer == NOT_FOUND_ANSWER
    assert llm.prompts == []
