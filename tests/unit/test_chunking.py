import pytest

from app.domain.chunking import chunk_pages


def words(n: int, start: int = 0) -> str:
    return " ".join(f"w{i}" for i in range(start, start + n))


def test_texto_curto_vira_um_unico_trecho():
    chunks = chunk_pages(["uma frase curta"], size=800, overlap=100)
    assert [(c.page, c.content) for c in chunks] == [(1, "uma frase curta")]


def test_texto_longo_tem_sobreposicao_e_cobre_tudo():
    chunks = chunk_pages([words(25)], size=10, overlap=3)

    assert [len(c.content.split()) for c in chunks] == [10, 10, 10, 4]
    assert chunks[0].content.split()[-3:] == chunks[1].content.split()[:3]
    assert chunks[-1].content.split()[-1] == "w24"


def test_pagina_vazia_e_ignorada_e_numeracao_preservada():
    chunks = chunk_pages(["primeira", "", "   \n ", "quarta"])
    assert [(c.page, c.content) for c in chunks] == [(1, "primeira"), (4, "quarta")]


def test_trecho_nunca_cruza_paginas():
    chunks = chunk_pages([words(5), words(5, start=100)], size=8, overlap=2)
    assert [c.page for c in chunks] == [1, 2]


def test_tamanho_exato_nao_gera_trecho_extra():
    assert len(chunk_pages([words(10)], size=10, overlap=3)) == 1


def test_sem_paginas_devolve_vazio():
    assert chunk_pages([]) == []


@pytest.mark.parametrize("size, overlap", [(0, 0), (10, 10), (10, -1)])
def test_parametros_invalidos(size, overlap):
    with pytest.raises(ValueError):
        chunk_pages(["texto"], size=size, overlap=overlap)
