# EduRAG: progresso

> Atualizado em 14/10/2026. Referência: [spec.md](spec.md).

## Resumo

- **Camada A (aplicação):** implementada e **validada ponta a ponta** com PostgreSQL + pgvector e Ollama reais (`qwen2.5:3b` e `nomic-embed-text`).
- **Qualidade da recuperação:** funciona, mas o limiar `MIN_SCORE` **não separa bem** perguntas do tema e fora do tema com esse modelo de embeddings (detalhes abaixo). Decisão tomada: aceitar a limitação e documentá-la na spec; quem segura as perguntas fora do tema é o prompt, não o limiar.
- **Camada B (operação):** não iniciada. Pela regra da spec, você escreve; a IA explica e revisa.

## O que foi feito

### Tarefas da seção 7

| Tarefa | Status | Onde está |
| --- | --- | --- |
| T1: Esqueleto | Feita | `pyproject.toml`, `app/main.py`, `app/config.py`, `app/logging_config.py` |
| T2: Containers | Feita e validada | `Dockerfile`, `docker-compose.yml`, `.env.example`, `scripts/pull-models.sh` |
| T3: Banco | Feita e validada | `app/db/models.py`, `app/db/migrations/versions/0001_initial.py` |
| T4: Portas e adaptadores | Feita e validada | `app/ports/`, `app/adapters/`, `tests/fakes.py`, `/ready` |
| T5: Chunking | Feita | `app/domain/chunking.py` |
| T6: Documentos | Feita e validada com PDF real | `app/api/routes_documents.py`, `app/domain/ingestion.py` |
| T7: Perguntas | Feita e validada com PDF real | `app/api/routes_ask.py`, `app/domain/qa.py`, `app/domain/prompts.py` |
| T8: Histórico | Feita | `GET /questions` |
| T9: Testes de integração | Feita | `tests/integration/` |
| T10: README | Feita | `README.md` |

### O que foi testado

**Automatizado** (`uv run pytest`): 49 testes, sendo 35 sem banco e 14 contra PostgreSQL real quando `TEST_DATABASE_URL` está definida. Na última rodada completa com Postgres, 46 passaram; os 3 testes novos dos adaptadores rodam sem banco. Cobertura de `domain/`: 99%. `ruff check` e `ruff format` limpos.

**Manual, com a stack completa** (Docker Compose, Ollama real):

| Teste | Resultado |
| --- | --- |
| Postgres não subia com `POSTGRES_PASSWORD` vazio | Causa encontrada; o compose agora recusa subir sem a senha, com mensagem clara |
| `/health` e `/ready` | 200 com tudo de pé |
| Upload de um currículo em PDF | `202`, depois `pronto`, 1 página, 1 trecho (~3.300 caracteres) |
| `/ask` "Do que se trata este documento?" nesse currículo | Respondeu "não encontrei": score 0,489, abaixo do `MIN_SCORE` 0,5 da época |
| Upload de um edital de teste de 3 páginas | `pronto`; fontes apontam para a página certa |
| Pergunta específica ("Até quando vão as inscrições?") | Resposta correta, citando a fonte `[1]`, fonte na página 2 (score 0,68) |
| Pergunta genérica ("Do que se trata este documento?") | Resposta correta (score 0,65 na página 1) |
| Pergunta fora do tema ("receita de bolo") | O LLM respondeu "Não encontrei...", mas o score do melhor trecho foi 0,60, acima do limiar |
| `DELETE /documents/{id}` | `204` |

### Mudanças feitas a partir dos testes (14/10/2026)

Registradas em [spec.md](spec.md), na seção "Decisões registradas durante a construção".

1. **Prefixos do `nomic-embed-text`.** `EmbeddingsPort` agora tem `embed_documents` e `embed_query`; o adaptador aplica os prefixos `search_document: ` e `search_query: ` (configuráveis, vazios para outros modelos).
2. **`LLM_NUM_CTX` (8192).** O Ollama cortava o prompt em silêncio na janela padrão (~4k tokens), e um trecho de 800 palavras já ocupa cerca de 1.200 tokens.
3. **`MIN_SCORE` de 0,5 para 0,45, e depois para 0,3.** Ver a ressalva e a seção sobre alucinação logo abaixo.
4. **`LLM_TIMEOUT_SECONDS` exposta no compose** e no `.env.example`.
5. **Validação do compose:** `POSTGRES_PASSWORD` passou a ser obrigatória.
6. **`# syntax=` removido do Dockerfile.** Ele forçava uma consulta ao registry em todo build e quebrava sem internet; nada no Dockerfile depende dele.

### Achado importante: o limiar não separa por relevância

Medido com o Ollama real:

| Pergunta (edital de teste) | Melhor score com prefixos |
| --- | --- |
| Do que se trata este documento? | 0,65 |
| Até quando vão as inscrições? | 0,68 |
| Receita de bolo de cenoura (fora do tema) | **0,60** |

Os prefixos subiram todos os scores, inclusive o de fora do tema, então a distância entre "relevante" e "irrelevante" continua pequena. Nenhum `MIN_SCORE` fixo separa os dois casos sem recusar perguntas genéricas legítimas. Hoje o sistema funciona porque o prompt manda o LLM responder "não encontrei" quando o contexto não tem a resposta, mas isso custa uma chamada ao LLM (lenta em CPU) e o RF06 ("sem chamar o LLM") só vale para scores baixos.

### Alucinação com pergunta hipotética (14/10/2026)

**Caso:** no currículo reenviado, a pergunta "Dado que Rafael Menezes é um desenvolvedor de software, como ele diria uma receita de bolo?" gerou uma resposta inventada (passos de "modelagem de dados", Spring, React...), citando o currículo como fonte.

**Por quê:** a pergunta menciona o dono do currículo, então a busca encontrou o currículo (score 0,56) e o limiar deixou passar. O prompt antigo só dizia "use somente o contexto"; o `qwen2.5:3b` tratou o pedido como tarefa criativa e usou o currículo como "inspiração". É um caso parecido com prompt injection: a pergunta empurra o modelo para fora do papel.

**O que foi feito:**

1. **Prompt em regras numeradas** (`app/domain/prompts.py`): só fatos do contexto; perguntas sobre o assunto do documento são válidas; pedidos de receitas, hipóteses, opiniões, textos criativos, "como ele faria" ou "imagine que" recebem a frase de recusa.
2. **Detecção de recusa mais estrita** (`app/domain/qa.py`): as fontes só são removidas quando a resposta é exatamente a frase de recusa. Uma primeira versão removia as fontes de respostas válidas que tinham a frase no final; isso foi corrigido e ganhou teste.
3. **`MIN_SCORE` padrão para 0,3.** No currículo reenviado, "Do que se trata este documento?" teve 0,44 e era recusada pelo limiar, enquanto as perguntas sobre bolo tinham 0,50 a 0,56. Com 0,3 o limiar fica só para os casos extremos, como a alternativa 1 decidiu.

**Resultado pela API (com `MIN_SCORE=0,3`):**

| Pergunta | Antes | Depois |
| --- | --- | --- |
| "...como ele diria uma receita de bolo?" | resposta inventada, com fonte | recusa, sem fontes |
| Do que se trata este documento? | recusa (limiar) | resposta correta, com fonte |
| Quais tecnologias Rafael domina? | resposta correta | resposta correta |
| Onde Rafael mora? | recusa | recusa (ver abaixo) |

**Limitações que continuam:**

- "Onde Rafael mora?" é recusada com os dois prompts, mesmo com a cidade escrita no currículo. O documento diz "Palmas, Tocantins" no cabeçalho, sem a palavra "mora", e o modelo de 3B não faz essa ligação. É limite do modelo, não do prompt.
- Um prompt reduz a alucinação, mas não a elimina: um modelo pequeno ainda pode ser convencido por perguntas mais elaboradas. A defesa de verdade é o item da F5 (defesa contra prompt injection e avaliação com Ragas).

## O que falta

### Para fechar a Camada A

- [x] **Limiar: alternativa 1 aceita (14/10/2026).** `MIN_SCORE` reduzido para 0,3 (limiar só em casos extremos), RF06 reescrito na spec ("Limitação conhecida") e fontes omitidas quando o próprio LLM recusa. Alternativas futuras: modelo multilíngue (`bge-m3`, exige migration e reindexação) ou reranker.
- [ ] **Trechos menores.** Testar `CHUNK_SIZE=300`, que costuma dar vetores mais focados. Exige reenviar os PDFs.
- [x] **Currículo antigo apagado** e reenviado com os vetores novos (com prefixos).
- [x] **`MIN_SCORE=0.3` no `.env`**; validado pela API (pergunta hipotética recusada, "Do que se trata" respondida).
- [ ] **Medir a latência real** do `qwen2.5:3b` na sua máquina e ajustar `LLM_TIMEOUT_SECONDS`.
- [x] **Mudanças commitadas** em commits separados por assunto (14/10/2026).
- [ ] **Atualizar o README** com a observação sobre prefixos e reenvio de PDFs, se quiser.
- [ ] **Pinar a versão do Ollama** no `docker-compose.yml` (hoje `latest`).
- [ ] **Revisar o código.** Leia e entenda cada arquivo antes de considerar a Camada A sua.

### Camada B (você aplica)

Ordem sugerida na spec. Cada fase já tem o ponto de encaixe pronto na aplicação.

- [ ] **F2: Pipeline segura.** GitHub Actions com ruff, pytest (serviço Postgres para `TEST_DATABASE_URL`), Semgrep ou Bandit, Trivy, gitleaks, Dependabot e proteção de branch. O repositório já está no GitHub: `rafelms/EduRAG`.
- [ ] **F3: Segredos e acesso.** SOPS ou Vault, API key ou JWT (middleware em `app/api/`) e rate limiting.
- [ ] **F4: Observabilidade.** `/metrics` para Prometheus, Grafana, Loki e OpenTelemetry. O `request_id` e os logs JSON já existem.
- [ ] **F5: LLMOps.** Langfuse em `app/adapters/ollama_llm.py`, Ragas na CI (o conjunto de perguntas de referência serve também para calibrar o limiar), defesa contra prompt injection em `app/domain/prompts.py`, mascaramento de CPF e e-mail e custo em tokens.
- [ ] **F6: Kubernetes.** k3s ou kind, manifests e Helm; `/health` e `/ready` viram as probes.
- [ ] **F7 (opcional): Nuvem e IaC.** Terraform.

## Como retomar

```bash
uv sync
uv run pytest                      # unitários + API em memória
docker compose up -d --build       # stack completa
./scripts/pull-models.sh           # só na primeira vez
```
