from app.domain.ingestion import IngestionService
from app.ports.repository import DocumentStatus
from tests.fakes import FakeEmbeddings, InMemoryRepository
from tests.pdfs import make_blank_pdf, make_pdf


def build(batch_size: int = 16):
    repo = InMemoryRepository()
    embeddings = FakeEmbeddings()
    service = IngestionService(
        repo, embeddings, chunk_size=800, chunk_overlap=100, batch_size=batch_size
    )
    return repo, embeddings, service


def test_pdf_com_texto_fica_pronto_e_grava_trechos_com_pagina():
    repo, _, service = build()
    doc = repo.create_document("edital.pdf")

    service.ingest(doc.id, make_pdf(["inscricoes ate 15 de outubro", "prova em dezembro"]))

    saved = repo.get_document(doc.id)
    assert saved.status == DocumentStatus.PRONTO
    assert saved.pages == 2
    assert [c.page for c in repo.chunks[doc.id]] == [1, 2]
    assert len(repo.chunks[doc.id][0].embedding) == 768


def test_pdf_sem_texto_vira_erro_com_motivo():
    repo, _, service = build()
    doc = repo.create_document("escaneado.pdf")

    service.ingest(doc.id, make_blank_pdf(2))

    saved = repo.get_document(doc.id)
    assert saved.status == DocumentStatus.ERRO
    assert "texto" in saved.error
    assert doc.id not in repo.chunks


def test_arquivo_corrompido_vira_erro_sem_levantar():
    repo, _, service = build()
    doc = repo.create_document("quebrado.pdf")

    service.ingest(doc.id, b"%PDF-1.4 isto nao e um pdf de verdade")

    assert repo.get_document(doc.id).status == DocumentStatus.ERRO


def test_falha_nos_embeddings_vira_erro():
    repo, embeddings, service = build()
    embeddings.embed_documents = lambda texts: (_ for _ in ()).throw(ConnectionError("ollama fora"))
    doc = repo.create_document("a.pdf")

    service.ingest(doc.id, make_pdf(["texto qualquer"]))

    saved = repo.get_document(doc.id)
    assert saved.status == DocumentStatus.ERRO
    assert "ConnectionError" in saved.error


def test_embeddings_sao_gerados_em_lotes():
    repo = InMemoryRepository()
    embeddings = FakeEmbeddings()
    service = IngestionService(repo, embeddings, chunk_size=2, chunk_overlap=0, batch_size=2)
    doc = repo.create_document("a.pdf")

    service.ingest(doc.id, make_pdf(["a b c d e f g"]))  # 4 trechos

    assert [len(call) for call in embeddings.calls] == [2, 2]
