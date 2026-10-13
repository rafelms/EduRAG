from tests.pdfs import make_blank_pdf, make_pdf

EDITAL = ["Informacoes gerais do concurso", "As inscricoes estarao abertas ate 15 de outubro"]


def upload(client, content: bytes, name: str = "edital.pdf", mime: str = "application/pdf"):
    return client.post("/documents", files={"file": (name, content, mime)})


def test_health_e_ready(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").status_code == 200


def test_ready_devolve_503_com_o_componente_que_falhou(client, fakes):
    fakes["embeddings"].available = False

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["failed"] == ["ollama"]


def test_upload_valido_responde_202_e_chega_a_pronto(client):
    response = upload(client, make_pdf(EDITAL))

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "processando"

    detail = client.get(f"/documents/{body['id']}").json()
    assert detail["status"] == "pronto"
    assert detail["pages"] == 2
    assert detail["filename"] == "edital.pdf"


def test_upload_de_outro_tipo_responde_400(client):
    assert upload(client, b"texto", "notas.txt", "text/plain").status_code == 400
    assert upload(client, b"nao sou pdf", "falso.pdf").status_code == 400


def test_upload_maior_que_o_limite_responde_413(client):
    big = b"%PDF-1.4\n" + b"0" * (1024 * 1024 + 1)
    assert upload(client, big).status_code == 413


def test_pdf_sem_texto_fica_com_erro(client):
    doc_id = upload(client, make_blank_pdf()).json()["id"]

    detail = client.get(f"/documents/{doc_id}").json()
    assert detail["status"] == "erro"
    assert detail["error"]


def test_listar_detalhar_e_excluir(client):
    doc_id = upload(client, make_pdf(EDITAL)).json()["id"]

    assert [d["id"] for d in client.get("/documents").json()] == [doc_id]
    assert client.delete(f"/documents/{doc_id}").status_code == 204
    assert client.get(f"/documents/{doc_id}").status_code == 404
    assert client.delete(f"/documents/{doc_id}").status_code == 404
    assert client.get("/documents").json() == []


def test_id_inexistente_responde_404(client):
    assert client.get("/documents/00000000-0000-0000-0000-000000000000").status_code == 404


def test_excluir_remove_os_trechos_da_busca(client):
    doc_id = upload(client, make_pdf(EDITAL)).json()["id"]
    client.delete(f"/documents/{doc_id}")

    answer = client.post("/ask", json={"question": "inscricoes ate quando"}).json()

    assert answer["sources"] == []


def test_pergunta_devolve_resposta_com_fonte_na_pagina_certa(client):
    doc_id = upload(client, make_pdf(EDITAL)).json()["id"]

    response = client.post(
        "/ask",
        json={"question": "inscricoes abertas ate quando", "document_ids": [doc_id], "top_k": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    top = body["sources"][0]
    assert (top["document_id"], top["filename"], top["page"]) == (doc_id, "edital.pdf", 2)
    assert 0 < top["score"] <= 1


def test_pergunta_fora_do_tema_nao_encontra_e_nao_chama_o_llm(client, fakes):
    upload(client, make_pdf(EDITAL))

    body = client.post("/ask", json={"question": "receita de bolo de cenoura"}).json()

    assert "Não encontrei" in body["answer"]
    assert body["sources"] == []
    assert fakes["llm"].prompts == []


def test_pergunta_invalida_responde_422(client):
    assert client.post("/ask", json={"question": "   "}).status_code == 422
    assert client.post("/ask", json={"question": "ok", "top_k": 0}).status_code == 422


def test_historico_paginado_com_latencia(client):
    upload(client, make_pdf(EDITAL))
    for question in ["inscricoes ate quando", "receita de bolo", "prova em dezembro"]:
        client.post("/ask", json={"question": question})

    page = client.get("/questions", params={"limit": 2, "offset": 0}).json()
    assert page["total"] == 3 and len(page["items"]) == 2
    assert page["items"][0]["question"] == "prova em dezembro"
    assert all(item["latency_ms"] >= 0 for item in page["items"])

    rest = client.get("/questions", params={"limit": 2, "offset": 2}).json()
    assert len(rest["items"]) == 1


def test_logs_tem_request_id_e_nao_vazam_conteudo_do_pdf(client, capfd):
    upload(client, make_pdf(["segredo-do-documento"]))

    response = client.get("/health", headers={"x-request-id": "abc123"})

    assert response.headers["x-request-id"] == "abc123"
    out = capfd.readouterr().out
    assert '"request_id": "abc123"' in out
    assert "segredo-do-documento" not in out
