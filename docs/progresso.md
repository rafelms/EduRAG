# EduRAG: progresso

> Sessão de 13/10/2026. Referência: [spec.md](spec.md).

## Resumo

A **Camada A** (seções 2 a 7 da spec) foi implementada por completo, de T1 a T10. A **Camada B** (seção 8) não foi iniciada: pela regra da spec, ela é escrita por você.

## O que foi feito

### Tarefas da seção 7

| Tarefa | Status | Onde está | Como foi verificado |
| --- | --- | --- | --- |
| T1: Esqueleto | Feita | `pyproject.toml`, `app/main.py`, `app/config.py`, `app/logging_config.py` | `/health` responde 200 nos testes |
| T2: Containers | Feita, falta validar a stack completa | `Dockerfile`, `docker-compose.yml`, `.env.example`, `scripts/pull-models.sh` | build da imagem ok, roda como `edurag` (não-root) |
| T3: Banco | Feita | `app/db/models.py`, `app/db/migrations/versions/0001_initial.py` | migration roda limpa num Postgres + pgvector vazio |
| T4: Portas e adaptadores | Feita | `app/ports/`, `app/adapters/`, `tests/fakes.py`, `/ready` | `/ready` dá 200 com tudo de pé e 503 `["ollama"]` com o Ollama falso desligado |
| T5: Chunking | Feita | `app/domain/chunking.py` | testes de texto curto, texto longo, página vazia, limites e parâmetros inválidos |
| T6: Documentos | Feita, falta validar com Ollama real | `app/api/routes_documents.py`, `app/domain/ingestion.py` | upload → `pronto` → trechos no Postgres (com embeddings falsos) |
| T7: Perguntas | Feita, falta validar com Ollama real | `app/api/routes_ask.py`, `app/domain/qa.py`, `app/domain/prompts.py` | página certa na fonte; "não encontrei" sem chamar o LLM |
| T8: Histórico | Feita | `GET /questions` | paginação, ordem e latência testadas |
| T9: Testes de integração | Feita | `tests/integration/` | 46 testes passando contra Postgres real; cobertura de `domain/` em 99% |
| T10: README | Feita | `README.md` | não testado por outra pessoa |

### Requisitos funcionais

Os requisitos RF01 a RF08 estão implementados e têm teste automatizado.

### Requisitos não funcionais

| Requisito | Situação |
| --- | --- |
| Configuração 100% por env | Feito (`pydantic-settings`); `.env.example` sem valores reais |
| Logs JSON com `request_id`, sem conteúdo dos PDFs | Feito; há um teste que garante que o texto do PDF não aparece nos logs |
| LLM, embeddings e banco atrás de portas | Feito; o domínio não importa nenhum adaptador |
| pytest com fakes, cobertura ≥ 70% em `domain/` | Feito (99%) |
| ruff e type hints | Feito; `ruff check` e `ruff format` limpos |
| Imagem slim, multi-stage, não-root | Feito |
| Respostas em português | Feito via prompt; não validado com o modelo real |

### Decisões tomadas durante a implementação

Estas decisões não estavam explícitas na spec. A regra 5 da spec pede para registrá-las nela.

1. **Tokens contados como palavras.** Os trechos têm 800 palavras com sobreposição de 100, configuráveis por `CHUNK_SIZE` e `CHUNK_OVERLAP`. Um trecho nunca cruza duas páginas, para que a citação seja sempre exata.
2. **`app/container.py`.** É um arquivo novo, fora da estrutura da spec. É ali que as portas são ligadas aos adaptadores (composition root), e é o que permite aos testes injetar os fakes.
3. **Score.** O score é a similaridade de cosseno (`1 - distância`). A busca só considera documentos com status `pronto`.
4. **Pergunta sem resposta.** Quando a resposta é "não encontrei", o histórico grava `model = "nenhum"` e a lista de fontes vazia.
5. **`/ask` com Ollama fora do ar.** A rota responde `502`. Isso não estava na spec.
6. **Formato de `/questions`.** A resposta é `{items, total, limit, offset}`, com `limit` até 100.
7. **Validação do upload.** O nome do arquivo precisa terminar em `.pdf` e o conteúdo precisa começar com `%PDF-`; senão a resposta é `400`. O limite de tamanho é lido só até `MAX_UPLOAD_MB + 1` byte.
8. **Migrations na subida.** O container roda `alembic upgrade head` antes de iniciar o uvicorn.
9. **Testes de API em dois modos.** Eles rodam sempre com um repositório em memória. Com `TEST_DATABASE_URL` definida, rodam também contra o Postgres. Nesse modo os testes apagam os dados das tabelas.

## O que falta

### Para fechar a Camada A

- [ ] **Validar a stack completa.** Rodar `docker compose up -d --build` e depois `./scripts/pull-models.sh`. Esse teste não foi feito porque baixa vários GB.
- [ ] **T6 com dados reais.** Enviar um PDF real e confirmar que ele chega a `pronto` com embeddings do `nomic-embed-text`.
- [ ] **T7 com dados reais.** Confirmar que uma pergunta sobre o PDF traz a página certa e que uma pergunta fora do tema dá "não encontrei".
- [ ] **Calibrar `MIN_SCORE`.** O valor padrão é 0.5, um chute. Ajuste olhando os scores reais.
- [ ] **Medir a latência do `qwen2.5:3b` em CPU.** Se passar de 300 s, aumente `LLM_TIMEOUT_SECONDS`.
- [ ] **Gerar o `uv.lock`.** Rode `uv sync` e versione o arquivo. O `uv` não estava instalado na sessão.
- [ ] **Git.** Rodar `git init`, fazer o primeiro commit e, de preferência, um commit por tarefa como a spec pede.
- [ ] **Atualizar a spec.** Registrar nela as decisões da seção anterior.
- [ ] **Pinar a versão do Ollama.** O `docker-compose.yml` usa `ollama/ollama:latest`; vale fixar uma versão.
- [ ] **Revisar o código.** Leia e entenda cada arquivo antes de considerar a Camada A sua.

### Camada B (você aplica)

- [ ] **F2: Pipeline segura.** GitHub Actions com ruff, pytest (com o serviço Postgres para `TEST_DATABASE_URL`), Semgrep ou Bandit, Trivy, gitleaks, Dependabot e proteção de branch.
- [ ] **F3: Segredos e acesso.** SOPS ou Vault, API key ou JWT (middleware em `app/api/`) e rate limiting.
- [ ] **F4: Observabilidade.** `/metrics` para Prometheus, Grafana, Loki e OpenTelemetry. O `request_id` e os logs JSON já existem.
- [ ] **F5: LLMOps.** Langfuse em `app/adapters/ollama_llm.py`, Ragas na CI, defesa contra prompt injection em `app/domain/prompts.py`, mascaramento de CPF e e-mail e custo em tokens.
- [ ] **F6: Kubernetes.** k3s ou kind, manifests e Helm; `/health` e `/ready` viram as probes.
- [ ] **F7 (opcional): Nuvem e IaC.** Terraform.

## Como retomar

```bash
uv sync
uv run pytest                     # unitários + API em memória
docker compose up -d postgres
TEST_DATABASE_URL=postgresql+psycopg://edurag:<senha>@localhost:5432/<banco_de_teste> \
  uv run pytest --cov=app/domain  # inclui Postgres real
```
