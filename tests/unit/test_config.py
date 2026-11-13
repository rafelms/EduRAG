"""A config impede a API de subir com um modelo do Claude fora da lista."""

import pytest
from pydantic import ValidationError

from app.adapters.claude_llm import ClaudeLLM
from app.adapters.ollama_llm import OllamaLLM
from app.config import Settings
from app.container import build_llm


def test_padrao_continua_no_ollama():
    settings = Settings()

    assert settings.llm_provider == "ollama"
    assert isinstance(build_llm(settings), OllamaLLM)


def test_claude_com_sonnet_5_monta_o_adaptador_do_claude():
    settings = Settings(
        llm_provider="claude", llm_model="claude-sonnet-5", anthropic_api_key="chave-falsa"
    )

    llm = build_llm(settings)

    assert isinstance(llm, ClaudeLLM)
    assert llm.model_name == "claude-sonnet-5"


@pytest.mark.parametrize(
    "model", ["claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-2", "qwen2.5:3b"]
)
def test_claude_com_outro_modelo_nao_sobe(model):
    with pytest.raises(ValidationError, match="não é permitido"):
        Settings(llm_provider="claude", llm_model=model, anthropic_api_key="chave-falsa")


@pytest.mark.parametrize("key", [None, ""])
def test_claude_sem_chave_nao_sobe(key):
    with pytest.raises(ValidationError, match="exige ANTHROPIC_API_KEY"):
        Settings(llm_provider="claude", llm_model="claude-sonnet-5", anthropic_api_key=key)


def test_modelo_vem_do_ambiente(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "claude")
    monkeypatch.setenv("LLM_MODEL", "claude-opus-5-5")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "chave-falsa")

    with pytest.raises(ValidationError):
        Settings()


def test_chave_nao_aparece_no_repr():
    settings = Settings(
        llm_provider="claude", llm_model="claude-sonnet-5", anthropic_api_key="sk-segredo"
    )

    assert "sk-segredo" not in repr(settings)
