# EduRAG: progresso

> Atualizado em 19/10/2026. Referência: [spec.md](spec.md).

## Resumo

- **Camada A (aplicação):** implementada e **validada ponta a ponta** com PostgreSQL + pgvector e Ollama reais (`qwen2.5:3b` e `nomic-embed-text`). Falta só a sua revisão do código.
- **Qualidade da recuperação:** funciona, mas o limiar `MIN_SCORE` **não separa bem** perguntas do tema e fora do tema com esse modelo de embeddings (detalhes abaixo). Decisão tomada: aceitar a limitação e documentá-la na spec; quem segura as perguntas fora do tema é o prompt, não o limiar.
- **Frontend (16/10/2026; na spec como RF09 e T11 desde 19/10/2026):** interface React + Tailwind em `frontend/`, servida por nginx no compose (porta 8080), pensada para o deploy na AWS. Validada ponta a ponta pelo proxy e conferida no navegador em 19/10/2026.
- **Camada B (operação):** em andamento. Etapas 0 a 4 da pipeline concluídas (ver [pipeline-plano.md](pipeline-plano.md)): CI de backend e frontend, `main` protegida e gitleaks como portão de segredos. A próxima é a 5 (SAST).

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
| T11: Interface web | Feita e conferida no navegador | `frontend/`, serviço `web` no `docker-compose.yml` |

### O que foi testado

**Automatizado** (`uv run pytest`), última rodada completa em 14/10/2026, com `TEST_DATABASE_URL` apontando para o banco `edurag_test` do Postgres do compose: **59 passaram, 0 pulados**. Cobertura de `domain/`: 99% (`qa.py` 98%). `ruff check` e `ruff format` limpos. Sem `TEST_DATABASE_URL`, os 14 testes de Postgres aparecem como pulados.

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
2. **Detecção de recusa** (`app/domain/qa.py`): as fontes são removidas quando o LLM recusa. Primeira versão: procurava a frase em qualquer ponto e apagava as fontes de respostas válidas que a tinham no final. Segunda versão: exigia a frase exata e deixava passar variações do modelo ("no documento", espaço duplo, `[1]` no fim). Versão atual, após revisão: recusa é uma resposta **curta (até 120 caracteres) que começa com "não encontrei"**, depois de normalizar espaços, maiúsculas, aspas e pontuação. Tem testes com 7 variações de recusa e 2 respostas válidas. Na recusa, o texto também é padronizado para a frase oficial, para não sobrar uma citação solta como `[1]` sem fontes. Limite conhecido: uma resposta parcial curta como "Não encontrei a data, mas a taxa é R$ 120 [1]" seria tratada como recusa e perderia as fontes.
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

### Revisão de código: `prompts.py` e `qa.py` (14/10/2026)

| Achado | Situação |
| --- | --- |
| Recusa do LLM com citação no fim ("Não encontrei... [1]") voltava com `[1]` solto e nenhuma fonte | **Corrigido:** o texto da recusa é padronizado para a frase oficial; teste cobre as variações |
| Detecção de recusa exigia a frase exata (apontado em revisão externa) | **Corrigido:** resposta curta que começa com "não encontrei", após normalização; 7 variações testadas |
| Regra 4 do prompt cita "instruções" como pedido a recusar, e editais têm instruções legítimas | **Testado, não se confirmou:** "Quais são as instruções para fazer a inscrição?" e "Como faço para me inscrever?" foram respondidas com fonte. Prompt mantido; observar em perguntas reais |
| Texto do PDF e a pergunta entram no prompt sem delimitação; um PDF com "ignore as regras" pode desviar o modelo | **Aberto, vai para a F5** (defesa contra prompt injection) |
| Resposta parcial curta ("Não encontrei X, mas Y [1]") é tratada como recusa e perde as fontes | **Aceito e documentado**; raro, e o custo é só a omissão das fontes |
| `str.format` com chaves `{}` no texto do PDF | **Sem problema:** `format` não reinterpreta os valores substituídos |
| Falha do Ollama no `/ask` devolve 502, mas a pergunta não vai para o histórico | **Aceito** para a Camada A; vira métrica de erro na F4 |

### Frontend web (16/10/2026)

Criado para o deploy na AWS, antes de estar na spec; registrado depois como RF09 e T11 (19/10/2026). O backend não mudou.

**Stack:** React 19 + Vite + Tailwind 4 + TypeScript, em `frontend/`. Sem bibliotecas além dessas.

**Telas:**

- **Documentos:** upload por clique ou arraste (vários PDFs), status atualizado a cada 3 s enquanto algum está em `processando`, exclusão com confirmação. Documentos prontos podem ser marcados para restringir a busca (`document_ids`); sem marcação, usa todos.
- **Perguntar:** contador até 2000 caracteres (mesmo limite do `AskRequest`), ajuste de `top_k` (1 a 20), cronômetro durante a geração. A resposta mostra as fontes com arquivo, página, similaridade em % e o trecho.
- **Histórico:** `GET /questions`, 10 por página.
- **Cabeçalho:** consulta `/ready` a cada 30 s e mostra qual componente caiu.

**Como fala com a API:** o frontend sempre chama `/api/*`. No desenvolvimento, o proxy do Vite repassa para `localhost:8000`; no container, o nginx repassa para `http://api:8000/` (tirando o `/api`). Mesma origem, então a API não precisa de CORS. Se um dia a API ficar em outro domínio, `VITE_API_BASE_URL` muda a base no build, e aí sim é preciso habilitar CORS na API.

**Arquivos:**

| Arquivo | Papel |
| --- | --- |
| `frontend/src/api.ts` | cliente e tipos, espelhando `app/api/schemas.py`; traduz o `detail` do FastAPI (texto ou lista de validação) em mensagem |
| `frontend/src/useDocuments.ts` | lista de documentos com polling durante o processamento |
| `frontend/src/components/` | `DocumentsPanel`, `AskPanel`, `HistoryPanel`, `SourceList`, `StatusIndicator` |
| `frontend/nginx.conf` | serve o build, fallback para `index.html`, proxy de `/api/` |
| `frontend/Dockerfile` | build em `node:24-alpine`, runtime em `nginx-unprivileged` (sem root, porta 8080) |
| `docker-compose.yml` | novo serviço `web`, porta `${WEB_PORT:-8080}` |

**Ajustes do nginx ligados à API:**

- `proxy_read_timeout 330s`: a geração pode levar até `LLM_TIMEOUT_SECONDS` (300 s). Sem isso, o padrão de 60 s do nginx cortaria as respostas lentas com 504.
- `client_max_body_size 25m`: acima do `MAX_UPLOAD_MB` (20), para o 413 vir da API, com a mensagem dela, e não do nginx.

**O que foi testado (stack completa, Ollama real):**

| Teste | Resultado |
| --- | --- |
| `npm run build` e `npm run lint` (oxlint) | limpos, sem avisos |
| `GET /` e rota inexistente (`/qualquer`) pelo nginx | 200 nos dois (fallback da SPA) |
| `/api/ready` e `/api/documents` pelo proxy | 200, mesmos dados da API direta |
| Upload de `.txt` pelo proxy | 400 "Apenas arquivos PDF são aceitos." |
| Pergunta vazia | 422 com lista de validação; o frontend mostra "a pergunta não pode ser vazia" |
| "Qual a formação acadêmica?" no currículo | resposta correta com fonte, em **~2 min**, sem 504 (confirma o timeout do nginx) |
| Visual no navegador | conferido à mão em 19/10/2026 |

**Riscos para o deploy na AWS:**

- **A API não tem autenticação.** Com o link, qualquer pessoa envia e apaga documentos e consome CPU do Ollama. Antes de expor, colocar pelo menos autenticação básica no nginx; a solução definitiva é a da F3 (API key ou JWT e rate limiting).
- **A porta 8000 da API continua publicada no compose.** Na AWS, abrir no security group só a porta do `web` (ou 80/443 atrás de um load balancer), ou tirar o `ports` do serviço `api`.
- **Sem HTTPS.** O nginx escuta só HTTP; o TLS deve ficar num ALB/CloudFront ou num certificado no próprio nginx.

## O que falta

### Para fechar a Camada A

- [x] **Limiar: alternativa 1 aceita (14/10/2026).** `MIN_SCORE` reduzido para 0,3 (limiar só em casos extremos), RF06 reescrito na spec ("Limitação conhecida") e fontes omitidas quando o próprio LLM recusa. Alternativas futuras: modelo multilíngue (`bge-m3`, exige migration e reindexação) ou reranker.
- [x] **Currículo antigo apagado** e reenviado com os vetores novos (com prefixos).
- [x] **`MIN_SCORE=0.3` no `.env`**; validado pela API (pergunta hipotética recusada, "Do que se trata" respondida).
- [x] **Detecção de recusa tolerante a variações** do modelo, com testes (ver "Alucinação com pergunta hipotética").
- [x] **Mudanças commitadas** em commits separados por assunto (14/10/2026).
- [x] **Ollama pinado** em `ollama/ollama:0.12.3`, a versão que estava rodando e foi validada (digest `sha256:926d40fd...`); a mudança entrou no commit `b771b5b`, cuja mensagem não a menciona.
- [x] **Revisão da IA em `prompts.py` e `qa.py`** (14/10/2026); achados na seção "Revisão de código" abaixo.
- [ ] **A sua revisão do código.** Continua sendo o principal: leia e entenda cada arquivo, começando por `app/domain/qa.py` e `app/domain/prompts.py`, que mudaram de forma sensível.
- [ ] *(Opcional)* **README:** observação sobre prefixos e reenvio de PDFs.

Itens movidos para a Camada B, onde viram trabalho medido em vez de ajuste avulso:

- **Trechos menores (`CHUNK_SIZE=300`)** → F5, como experimento comparado com Ragas.
- **Latência do LLM** → F4, como métrica em painel. Ponto de partida, do histórico em `questions` (14/10/2026): perguntas que chamam o `qwen2.5:3b` levaram de 2,2 s a 140 s, mediana 16,5 s (27 perguntas); recusas pelo limiar, de 37 a 100 ms. O máximo de 140 s está perto do `LLM_TIMEOUT_SECONDS` de 300 s.

### Frontend

- [x] **Conferir o visual no navegador** (`http://localhost:8080`), em 19/10/2026.
- [x] **Registrar na spec** como RF09 e T11 (19/10/2026).
- [ ] **Testes automatizados do front**, para o RF09 cumprir a regra da seção 2 da spec (e a Etapa 2 do plano).
- [ ] **Autenticação antes de expor na AWS** (básica no nginx como paliativo; F3 como solução).
- [ ] **Fechar a porta 8000 da API** no ambiente da AWS e colocar HTTPS na frente do `web`.

### Camada B (você aplica)

Ordem sugerida na spec. Cada fase já tem o ponto de encaixe pronto na aplicação.

- [ ] **F2: Pipeline segura** (em andamento: etapas 0 a 4 feitas, ver [pipeline-plano.md](pipeline-plano.md)). GitHub Actions com ruff, pytest (serviço Postgres para `TEST_DATABASE_URL`), Semgrep ou Bandit, Trivy, gitleaks, Dependabot e proteção de branch. O repositório já está no GitHub: `rafelms/EduRAG`.
- [ ] **F3: Segredos e acesso.** SOPS ou Vault, API key ou JWT (middleware em `app/api/`) e rate limiting.
- [ ] **F4: Observabilidade.** `/metrics` para Prometheus, Grafana, Loki e OpenTelemetry. O `request_id` e os logs JSON já existem. Inclui o painel de latência do LLM (veio da Camada A) e um alerta perto do `LLM_TIMEOUT_SECONDS`.
- [ ] **F5: LLMOps.** Langfuse em `app/adapters/ollama_llm.py`, Ragas na CI (o conjunto de perguntas de referência serve também para calibrar o limiar), defesa contra prompt injection em `app/domain/prompts.py`, mascaramento de CPF e e-mail e custo em tokens. Inclui o experimento de `CHUNK_SIZE` (300 contra 800), medido com o conjunto de referência (veio da Camada A).
- [ ] **F6: Kubernetes.** k3s ou kind, manifests e Helm; `/health` e `/ready` viram as probes.
- [ ] **F7 (opcional): Nuvem e IaC.** Terraform.

## Como retomar

```bash
uv sync
uv run pytest                      # unitários + API em memória
docker compose up -d --build       # stack completa; interface em localhost:8080
./scripts/pull-models.sh           # só na primeira vez
cd frontend && npm install && npm run dev   # frontend em modo dev (localhost:5173)
```
