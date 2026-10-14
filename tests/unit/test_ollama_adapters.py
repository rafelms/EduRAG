import json

import httpx

from app.adapters.ollama_embeddings import OllamaEmbeddings
from app.adapters.ollama_llm import OllamaLLM


def _mock_client(captured: list[dict], reply: dict) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(json.loads(request.content))
        return httpx.Response(200, json=reply)

    return httpx.Client(base_url="http://ollama", transport=httpx.MockTransport(handler))


def test_prefixos_distintos_para_documentos_e_perguntas():
    sent: list[dict] = []
    adapter = OllamaEmbeddings(
        "http://ollama", "nomic-embed-text", "search_document: ", "search_query: "
    )
    adapter._client = _mock_client(sent, {"embeddings": [[0.1], [0.2]]})

    adapter.embed_documents(["trecho a", "trecho b"])
    adapter._client = _mock_client(sent, {"embeddings": [[0.3]]})
    assert adapter.embed_query("pergunta") == [0.3]

    assert sent[0]["input"] == ["search_document: trecho a", "search_document: trecho b"]
    assert sent[1]["input"] == ["search_query: pergunta"]


def test_sem_prefixo_o_texto_vai_intacto():
    sent: list[dict] = []
    adapter = OllamaEmbeddings("http://ollama", "bge-m3")
    adapter._client = _mock_client(sent, {"embeddings": [[0.1]]})

    adapter.embed_documents(["trecho"])

    assert sent[0]["input"] == ["trecho"]


def test_llm_envia_a_janela_de_contexto_configurada():
    sent: list[dict] = []
    llm = OllamaLLM("http://ollama", "qwen2.5:3b", num_ctx=6000)
    llm._client = _mock_client(sent, {"response": " ok "})

    assert llm.generate("oi") == " ok "
    assert sent[0]["options"]["num_ctx"] == 6000
