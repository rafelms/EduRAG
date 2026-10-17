# Estudo — GitHub Actions

Anotações de estudo da pipeline. O plano das etapas está em [pipeline-plano.md](pipeline-plano.md); o workflow, em [ci.yml](../.github/workflows/ci.yml).

## Estrutura do workflow

| Chave | O que faz |
| --- | --- |
| `name` (topo) | Nome do workflow na aba Actions. Um `#` é só comentário e não vira nome. |
| `on` | Quando o workflow dispara. `push:` vazio dispara em qualquer push, de qualquer branch; `pull_request` com `branches: [main]` só em PR para a `main`. |
| `jobs` | Os trabalhos do workflow. Sem `needs`, rodam em paralelo, cada um numa máquina nova. |
| `runs-on` | A máquina do job. `ubuntu-24.04` fixa a versão; `ubuntu-latest` muda sozinha quando sai uma nova. |
| `steps` | Lista de passos do job (cada item começa com `-`). Rodam em sequência; se um falha, os seguintes não rodam. |
| `name` (step) | Opcional; é o rótulo do step no log. Sem ele, o GitHub mostra o comando cru. |

## `uses` × `run`

- `uses` chama uma action pronta, que é código de outra pessoa (por exemplo, o instalador do uv).
- `run` executa um comando no terminal do runner, como você faria na sua máquina.
- `with` passa parâmetros para uma action, por exemplo `enable-cache: true`.
- `env` define variáveis de ambiente. Pode ficar no step, no job ou no workflow inteiro.

Um step tem **um** `uses` **ou** um `run`, nunca os dois, e cada chave aparece uma vez só. Em YAML, uma chave repetida sobrescreve a anterior.

## Backend: o que cada passo faz

- **Cache do setup-uv:** guarda os pacotes baixados entre execuções e deixa a CI mais rápida. A chave do cache é o `uv.lock`: se o lock muda, o cache é refeito.
- **`uv sync --locked`:** lê o `pyproject.toml` e o `uv.lock`, instala o Python 3.12 se faltar e cria o `.venv` com as dependências, incluindo as de dev (pytest e ruff). O `--locked` falha se o lock estiver desatualizado, em vez de atualizá-lo em silêncio.
- **`uv run ...`:** executa o comando dentro desse `.venv`.
- **`ruff format --check`:** só verifica, e falha se algo estiver fora do padrão. Na CI você quer saber do problema, não corrigi-lo automaticamente.
- **Ordem:** o lint vem antes dos testes porque é mais rápido e falha cedo.

## Service containers (Postgres na CI)

- **O que é:** `services` sobe um container ao lado do job e o derruba no fim. É o equivalente ao `postgres` do compose, só que descartável.
- **Senha no YAML:** aqui é aceitável, porque o banco nasce e morre com o job e não guarda nada real. Segredo de verdade nunca vai no arquivo.
- **`ports: 5432:5432`:** expõe o banco em `localhost` no runner.
- **`options` com `--health-cmd`:** faz o GitHub esperar o banco ficar pronto antes dos steps. Sem isso, os testes falham de forma aleatória.
- **Migrations:** não precisam de step próprio, porque o `tests/integration/conftest.py` roda `alembic upgrade head`, e a migration inicial cria a extensão `vector`.

## Artefatos

`actions/upload-artifact` guarda arquivos gerados no job, como o `coverage.xml`. Eles aparecem no campo **Artifacts** do Summary da execução.

## Versões das actions

- Toda action precisa de `@versão`.
- **Tag** (`@v7`) é legível, mas o dono pode mover a tag para outro código.
- **SHA** (`@<commit>`) é imutável. É o que a Etapa 6 pede, por segurança de cadeia de suprimentos.
- Desde a v8, o `setup-uv` não publica mais tags de major (`@v10` não existe), só tags completas e imutáveis (`@v10.3.0`). Foi uma decisão de segurança, depois do ataque ao `tj-actions`, em que uma tag de major foi movida para código malicioso.
- Actions antigas rodam em versões de Node aposentadas e geram aviso. O Dependabot avisa quando sai versão nova.
