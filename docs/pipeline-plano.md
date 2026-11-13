# EduRAG — Plano de implementação (pipeline → AWS com Terraform → observabilidade)

> Atualizado em 12/11/2026. Referências: [spec.md](spec.md), [progresso.md](progresso.md) e [MISSION.md](estudo/MISSION.md).
> Regra da Camada B: **você escreve os workflows, o Terraform e o código**; a IA explica e revisa.

## Visão geral

A pipeline é construída em portões: cada etapa só é adicionada depois que a anterior está verde, e **nada chega à AWS sem passar por testes e scans**.

**Escopo redefinido em 12/11/2026:** o objetivo da reta final é a experiência de deploy na AWS, a infraestrutura como código (Terraform) e a observabilidade (Prometheus + Grafana). O ambiente de produção é **privado e temporário**: só o Rafael acessa, e ele é destruído no fim da trilha. Por isso, a segurança de exposição pública (login, cota, CORS) saiu do caminho e deu lugar a rede fechada, segredos fora do repositório e teto de gastos.

```mermaid
flowchart LR
    PR[Push / Pull Request] --> Q[Qualidade<br/>ruff, pytest, build do front]
    Q --> S[Segurança no código<br/>gitleaks, Semgrep, deps, IaC]
    S --> B[Build das imagens<br/>api + front]
    B --> T[Trivy nas imagens<br/>falha em CRITICAL]
    T -->|só na main| P[Publicar<br/>GHCR]
    P -->|só na main| D[Deploy no EC2<br/>via SSM]
    D --> SM[Smoke test<br/>/ready]
    SM --> O[Prometheus + Grafana<br/>métricas e alertas]
```

| Bloco | Etapas | Resultado |
| --- | --- | --- |
| A — Integração contínua | 0 a 3 | Todo PR testado; `main` protegida |
| B — Segurança na pipeline | 4 a 7 | Segredos, código, dependências e imagens verificados |
| C — Publicação | 8 | Imagens versionadas num registro |
| D — Pronto para a nuvem | 9 | Segredos auditados, teto de gastos e LLM na nuvem |
| E — Infraestrutura e entrega na AWS | 10 e 11 | Infra em Terraform; deploy automático com rollback |
| F — Observabilidade | 12 a 14 | Métricas, painéis e alertas versionados |
| G — Encerramento | 15 | Evidências guardadas e `terraform destroy` |

---

## Bloco A — Integração contínua

### Etapa 0 — Preparação

- [x] Registrar o frontend na spec: mover "Interface web" de *Fora de escopo* para os requisitos (RF09) e a tarefa (T11).
- [x] Confirmar que nenhum `.env` real está no repositório nem no histórico (`git log --all -- .env`).

*Pronto quando:* a spec descreve o que existe no código.

### Etapa 1 — CI do backend

- [x] Workflow disparado em `push` e `pull_request`.
- [x] Checkout → instalar `uv` (com cache) → `uv sync` → `ruff check` e `ruff format --check`.
- [x] `pytest` com um *service container* `pgvector/pgvector` e `TEST_DATABASE_URL` apontando para ele, rodando as migrations antes.
- [x] Relatório de cobertura como artefato do job.

*Pronto quando:* os 59 testes passam no GitHub, **0 pulados**.
*Para estudar:* sintaxe de workflow (`on`, `jobs`, `steps`), `services`, cache de dependências.

### Etapa 2 — CI do frontend

- [x] Job separado, rodando em paralelo ao do backend.
- [x] `npm ci` (nunca `npm install` na CI) → lint → build.
- [ ] Testes, se houver. (ainda não há testes no front)

*Pronto quando:* os dois jobs ficam verdes no mesmo PR.
*Para estudar:* jobs paralelos, `needs`, por que `npm ci` usa o lockfile.

### Etapa 3 — Proteção da branch `main`

- [x] Exigir PR para entrar na `main` (sem push direto).
- [x] Exigir os checks das etapas 1 e 2 como obrigatórios.

*Pronto quando:* um PR com teste quebrado não consegue ser mesclado.
**A partir daqui, toda mudança entra por PR**, inclusive as próximas etapas.

---

## Bloco B — Segurança na pipeline

Para cada ferramenta: primeiro rodar em modo de relatório, corrigir o que aparecer, **depois** transformar em portão que falha o build. E sempre provar o bloqueio com um PR proposital.

### Etapa 4 — Segredos (gitleaks)

- [x] Job do gitleaks em todo PR (`.github/workflows/security.yml`, job `gitleaks`, check obrigatório no ruleset `protege-main`).
- [x] Uma varredura única em **todo o histórico** do repositório (gitleaks v8.30.1 via Docker, `--log-opts="--all"`): nenhum achado.

*Teste de bloqueio:* PR com uma chave falsa no formato de chave da AWS → pipeline falha.
**Provado em 19/10/2026 ([PR #6](https://github.com/rafelms/EduRAG/pull/6)):** [`gitleaks` falhou](https://github.com/rafelms/EduRAG/actions/runs/39280762881/job/118154214397) com `aws-access-token` e comentou na linha da chave; `backend` e `frontend` passaram; merge bloqueado. O PR foi fechado sem merge. A chave de exemplo da AWS (`...EXAMPLE`) **não** serve para essa prova, porque a regra tem uma exceção para ela.
*Para estudar:* por que um segredo apagado num commit posterior continua vazado.

### Etapa 5 — Análise estática (SAST)

- [x] Semgrep cobrindo Python e TypeScript (`p/default`, job `semgrep` no `security.yml`, check obrigatório no ruleset `protege-main`).
- [x] Resultados enviados para a aba *Security* do GitHub (formato SARIF).

*Teste de bloqueio:* PR com SQL montado por concatenação de string → apontado.
**Provado em 20/10/2026 ([PR #10](https://github.com/rafelms/EduRAG/pull/10)):** `semgrep` falhou com `avoid-sqlalchemy-text` na linha 7 de `app/teste_sast.py`; `backend`, `frontend` e `gitleaks` passaram; merge bloqueado. O PR foi fechado sem merge. O portão barra só `--severity ERROR`; os avisos restantes viraram a lista de tarefas da etapa 6.
*Para estudar:* SAST × DAST, falso positivo e como suprimir com justificativa.

### Etapa 6 — Dependências

**Concluída em 04/11/2026** ([PR #38](https://github.com/rafelms/EduRAG/pull/38), cooldown). Registros: [0005](estudo/learning-records/0005-trivy-e-npm-audit-provados.md), [0007](estudo/learning-records/0007-primeira-rodada-do-dependabot.md) e [0009](estudo/learning-records/0009-cooldown-e-o-custo-da-espera.md). Aulas: [0004](estudo/lessons/0004-vulnerabilidades-com-trivy.html) (portão de vulnerabilidades), [0005](estudo/lessons/0005-cadeia-de-suprimentos.html) (cadeia de suprimentos) e [0007](estudo/lessons/0007-cooldown-na-pratica.html) (cooldown na prática).

*Parte 1: portão de vulnerabilidades (aula 0004)*
- [x] Corrigir o CRITICAL que o Trivy já achava (`certifi 2026.7.22` → `2026.10.19`): [PR #12](https://github.com/rafelms/EduRAG/pull/12).
- [x] `trivy fs` (job `trivy-fs`, `trivy-action` fixada por SHA, falha em HIGH/CRITICAL com `ignore-unfixed`) e `npm audit` (job `npm-audit`, `--audit-level=high`) no `security.yml`, os dois como checks obrigatórios do `protege-main`: [PR #13](https://github.com/rafelms/EduRAG/pull/13).

*Teste de bloqueio:* PR adicionando uma versão antiga e vulnerável de alguma biblioteca → pipeline falha.
**Provado em 23/10/2026 ([PR #14](https://github.com/rafelms/EduRAG/pull/14)):** [`trivy-fs` falhou](https://github.com/rafelms/EduRAG/actions/runs/39982005609/job/120511410590) com `pyyaml 5.3` (2 CRITICAL) no `uv.lock` e `lodash 4.17.20` (2 HIGH) no `package-lock.json`; [`npm-audit` falhou](https://github.com/rafelms/EduRAG/actions/runs/39982005609/job/120511411002) com `lodash`; `backend`, `frontend` e `gitleaks` passaram; merge bloqueado. O PR foi fechado sem merge. Na primeira tentativa, o `backend` caiu por `uv.lock` fora de sincronia (faltou `uv lock`) e o Trivy viu o `uv.lock` limpo: vermelho pelo motivo errado não vale como prova.

*Parte 2: cadeia de suprimentos (aula 0005)*
- [x] Fixar por SHA todas as actions de `ci.yml` e `security.yml` (o Semgrep acusava 12 usos por tag), com o comentário `# vX.Y.Z`: [PR #17](https://github.com/rafelms/EduRAG/pull/17).
- [x] Cooldown no uv (`exclude-newer = "7 days"`) e, junto, `cooldown` com `default-days: 7` no bloco `uv` do `dependabot.yml`, para o Dependabot não propor mínimos que o uv ainda não aceita. O uv novo no `Dockerfile` entrou no PR #29: [PR #38](https://github.com/rafelms/EduRAG/pull/38), mesclado em 04/11. O lock ganhou só o bloco `[options]`. No caminho, o `trivy-fs` barrou a `pypdf 6.21.2` (7 HIGH); a correção veio no #42 do Dependabot, com versões de menos de 7 dias, e exigiu uma isenção temporária por pacote (`pypdf`, `python-multipart`), **removida em 12/11** ([PR #47](https://github.com/rafelms/EduRAG/pull/47)).
- [x] `.github/dependabot.yml` para Python (`uv`), npm, Docker e GitHub Actions (é arquivo de configuração, não job): [PR #18](https://github.com/rafelms/EduRAG/pull/18). Primeira rodada em 27/10/2026: 8 PRs (#19 a #26), todos com merge em 28/10; o primeiro foi o [PR #25](https://github.com/rafelms/EduRAG/pull/25). O *Insights → Dependency graph → Dependabot* leu os 4 blocos sem erro. O #20 e o #23 levaram o frontend para a Node 26 e a CI foi alinhada no [PR #27](https://github.com/rafelms/EduRAG/pull/27).

*Pronto quando:* o Semgrep não acusa mais cadeia de suprimentos e o Dependabot abriu o primeiro PR.
*Para estudar:* SCA, CVE, por que fixar as actions é segurança de cadeia de suprimentos (caso real: o ataque à `trivy-action` em março de 2026).

### Etapa 7 — Build e scan das imagens

Aula: [0006](estudo/lessons/0006-build-e-scan-de-imagens.html). Situação medida em 28/10/2026 (Trivy 0.76.1): `api` e `front` com 0 CRITICAL; as duas já rodam sem root (uid 10001 e 101); `api` com 44 HIGH sem correção e `front` com 3 HIGH com correção (eram 44 em 23/10, antes da base 1.31).

**Concluída em 30/10/2026.** Registro: [0008](estudo/learning-records/0008-imagens-com-portao-provado.md).

- [x] **PR 1 (`ci/imagem-api`):** novo `.github/workflows/build.yml` com o job `imagem-api`: checkout → Buildx → build (`push: false`, `load: true`, cache `type=gha` com `scope` próprio) → `trivy image` falhando em CRITICAL → checagem de não-root (`id -u` diferente de `0`). Actions fixadas por SHA desde o início: [PR #32](https://github.com/rafelms/EduRAG/pull/32) (e [PR #33](https://github.com/rafelms/EduRAG/pull/33), que desliga o build record).
- [x] **PR 2 (`ci/imagem-front`):** job `imagem-front` (contexto `frontend/`, Nginx servindo o build do React), e os dois jobs como checks obrigatórios do `protege-main`: [PR #34](https://github.com/rafelms/EduRAG/pull/34). O portão achou um CRITICAL real na base 1.31 (CVE-2026-111497, `brotli-libs`), corrigido no mesmo PR com `apk upgrade`.
- [x] **PR 3 (provas):** `frontend/Dockerfile` com `nginx-unprivileged:1.21-alpine` (9 CRITICAL, constrói e sobe) → `imagem-front` falha no Trivy; `USER edurag` comentado no `Dockerfile` → `imagem-api` falha na checagem de não-root. Cada prova num PR descartável, fechado sem merge.

**Provado em 30/10/2026:** [PR #35](https://github.com/rafelms/EduRAG/pull/35): `imagem-api` falhou na checagem de não-root (`uid: 0`), e o `semgrep` também barrou com `dockerfile.security.missing-user`. [PR #36](https://github.com/rafelms/EduRAG/pull/36): `imagem-front` falhou no Trivy (Alpine 3.15.4, 9 CRITICAL). Os dois ficaram bloqueados e foram fechados sem merge.
*Estudo slim × completa (30/10):* `python:3.12` tem 1,62 GB, 454 HIGH e 16 CRITICAL; `python:3.12-slim` tem 180 MB, 44 HIGH e 0 CRITICAL. Os 44 HIGH do `api` são todos da base.

*Pronto quando:* as imagens só existem se passaram no scan (a publicação fica para a etapa 8, que reaproveita este build e o cache).
*Para estudar:* camadas de imagem, por que imagem base slim reduz vulnerabilidades.

---

## Bloco C — Publicação

### Etapa 8 — Publicar no GHCR

Aula: [0008](estudo/lessons/0008-publicar-no-ghcr.html). Desenho: jobs `publica-api` e `publica-front` no `build.yml`, com `needs` no portão da mesma imagem, só em push na `main` e com `packages: write` só neles.

**Concluída em 04/11/2026** ([PR #40](https://github.com/rafelms/EduRAG/pull/40)). Registro: [0010](estudo/learning-records/0010-publicacao-no-ghcr.md).

- [x] Só na `main` e só depois do portão da mesma imagem (`needs` + `if` de push na `main`). Os portões de código já foram exigidos no PR pelo ruleset.
- [x] Login com o `GITHUB_TOKEN` (sem criar segredo novo).
- [x] Tag com o SHA do commit (e `latest` só como apelido).

**Conferido em 12/11/2026:** no PR, os jobs `publica-*` ficam `skipped`; na `main`, os 4 merges desde o #40 publicaram `ghcr.io/rafelms/edurag-api` e `edurag-front` com a tag do SHA (`cd809cb…` é a atual, com `latest`). Os pacotes são públicos. Cada tag é um *image index* com a imagem amd64 e a atestação de proveniência.
*Ponto em aberto:* o `publica-*` refaz o build em vez de enviar a imagem escaneada. Com o cache o digest sai igual (visto em 12/11), mas não é garantido; publicar o mesmo digest fica como melhoria.

*Pronto quando:* cada merge na `main` gera uma imagem rastreável até o commit.
*Para estudar:* por que tag por SHA permite rollback e `latest` não.

---

## Bloco D — Pronto para a nuvem

### Etapa 9 — Segredos, teto de gastos e LLM na nuvem

**Em andamento.** Aula [0009](estudo/lessons/0009-antes-de-expor.html) (Console da Anthropic). Esta etapa foi **enxugada em 12/11/2026**: como o ambiente é privado, a proteção contra visitantes passa a ser a rede fechada da etapa 10, e não login no app. As antigas aulas 0011 a 0013 (autenticação, cota, CORS) saíram do caminho (ver [Fora do caminho](#fora-do-caminho)).

- [x] **Auditoria de segredos no histórico (12/11/2026).** Registro: [0011](estudo/learning-records/0011-auditoria-de-segredos.md).
  - gitleaks v8.21.2 em `--all`, mais os *heads* dos 8 PRs fechados sem merge (#1, #3, #6, #9, #10, #14, #35, #36), que continuam públicos em `refs/pull/N/head`: 73 commits, **1 achado**, a chave AWS falsa do PR #6 (`config-falsa.env`, a prova da etapa 4).
  - *Secret scanning* do GitHub: 0 alertas. O `.env` nunca foi commitado (`git log --all -- .env` vazio) e só tem variáveis de configuração e a senha local do Postgres.
  - Busca manual (o gitleaks não pega senha genérica): só `edurag:edurag` no Postgres efêmero da CI (aceitável: o banco morre com o job) e o padrão `change-me` no `app/config.py`.
- [ ] **`fix/config-sem-default`:** tirar o valor padrão de `database_url` em `app/config.py` (hoje `postgresql+psycopg://edurag:change-me@localhost…`). Sem padrão, a API falha ao subir sem `DATABASE_URL`, em vez de tentar uma senha conhecida. Conferir se os testes continuam passando.
- [x] **Aula 0009, Console (13/11/2026):** workspace `edurag`, teto de **US$ 5/mês** na organização e no workspace, limites do Sonnet 5 (15 mil entrada, 4 mil saída, 5 req/min), chave `edurag-dev` só no `.env`. Registro: [0012](estudo/learning-records/0012-teto-de-gastos-e-sonnet-5-fixo.md).
- [ ] **Aula 0010, `feat/claude-llm` (código escrito pela IA, a pedido dele):** adaptador `ClaudeLLM`, escolhido por `LLM_PROVIDER` (`ollama` local, `claude` na nuvem). **Só `claude-sonnet-5`**: allowlist na config (a API não sobe com outro modelo), sem `fallbacks`, sem ferramentas. Erros da API (teto `400`/`429`, rede) viram `LLMUnavailableError` → `502`. O `/ready` separa `embeddings` e `llm`. `top_k` máximo de 20 para 10. Tokens de cada chamada no log. Testes com cliente falso; a CI não usa chave real.
- [x] **Embeddings na nuvem:** Ollama só com o `nomic-embed-text` (decidido em 13/11). Medir a RAM na etapa 10.

*Pronto quando:* nenhum segredo real no histórico (feito), teto de gastos ativo e a API responde com o Claude na sua máquina.

---

## Bloco E — Infraestrutura e entrega na AWS

### Etapa 10 — Base na AWS com Terraform

Antes, a base seria feita à mão. Agora ela é **código**: tudo que for criado por `apply` some com `destroy` na etapa 15, sem recurso esquecido gerando cobrança.

*Bootstrap (à mão, uma vez, documentado):*
- [ ] Alerta de orçamento (AWS Budgets) **no primeiro dia**, antes de qualquer recurso. Depois ele entra no Terraform com um bloco `import`: é a primeira aula de `terraform import`.
- [ ] Root com MFA e guardado; usuário do dia a dia (IAM Identity Center ou IAM) com MFA. Credencial local por `aws sso login` ou perfil, nunca access key no repositório.
- [ ] Bucket S3 do *state* (versionado, criptografado, bloqueio de acesso público), com trava nativa do S3 (`use_lockfile = true`, sem DynamoDB).

*Terraform (pasta `infra/`, PR `infra/base`):*
- [ ] EC2 Amazon Linux 2023 (já vem com o agente do SSM) na VPC padrão, com *instance profile* `AmazonSSMManagedInstanceCore`. Tamanho de partida: `t3.medium` (Postgres, API, nginx, Ollama de embeddings, Prometheus e Grafana na mesma máquina); medir a RAM e ajustar. Disco gp3 e `user_data` instalando Docker e o plugin do compose.
- [ ] **Security group sem nenhuma regra de entrada.** Acesso só pelo túnel do SSM (`AWS-StartPortForwardingSession`) para a interface (8080) e o Grafana (3000). **Decidido em 13/11/2026: túnel do SSM**, nenhuma porta aberta.
- [ ] Provedor **OIDC** do GitHub e uma *role* com permissão mínima: `ssm:SendCommand` só nessa instância e no documento `AWS-RunShellScript`, e leitura do resultado. Condição no `sub`: só a `main` do `rafelms/EduRAG`.
- [ ] Parâmetros no **SSM Parameter Store** (`SecureString`) para a chave `edurag-prod` do Claude, a senha do Postgres e a senha do Grafana. **O valor é gravado à mão** (`aws ssm put-parameter`); o Terraform só dá à instância permissão de ler esses nomes. Valor de segredo em recurso do Terraform vai parar no *state*.
- [ ] **Registro: GHCR, sem ECR.** Os pacotes já são públicos e o EC2 puxa sem credencial (registro [0010](estudo/learning-records/0010-publicacao-no-ghcr.md)). O ECR acrescentaria custo e uma permissão sem ganho para um ambiente temporário.
- [ ] **Portão de IaC na CI:** `terraform fmt -check`, `terraform validate` (com `init -backend=false`, sem credencial) e `trivy config infra/` falhando em HIGH/CRITICAL, como check obrigatório. *Teste de bloqueio:* PR abrindo a porta 22 para `0.0.0.0/0` → pipeline falha.

*Pronto quando:* `terraform apply` sobe a máquina do zero, você abre a interface pelo túnel do SSM e um `nmap` de fora não acha nenhuma porta aberta.
*Para estudar:* *state* e por que ele é sensível, `plan` × `apply`, IAM e menor privilégio, OIDC × access keys, SSM Session Manager × SSH.

### Etapa 11 — Deploy contínuo

- [ ] `docker-compose.prod.yml`: imagens do GHCR pela tag do SHA (sem `build`), API sem porta publicada (só o `web` fala com ela pela rede interna), segredos lidos do Parameter Store no deploy, nunca de um `.env` versionado.
- [ ] Job `deploy` no `build.yml`, só na `main` e com `needs` na publicação: autentica via OIDC e manda pelo SSM `docker compose pull` + `up -d` com a tag do commit.
- [ ] Smoke test chamando `/ready`; se falhar, voltar para a tag anterior.

*Teste de bloqueio:* PR que quebra o `/ready` de propósito → o deploy volta sozinho para a tag anterior.
*Pronto quando:* um merge na `main` aparece no ar sozinho, e um deploy quebrado volta sozinho.
*Para estudar:* entrega contínua × deploy contínuo, *environments* com aprovação (pendência do registro 0004).

---

## Bloco F — Observabilidade (F4)

Fecha o que a Camada A deixou pendente: o painel de latência do LLM e o alerta perto do `LLM_TIMEOUT_SECONDS` ([progresso.md](progresso.md)).

### Etapa 12 — Métricas na API

- [ ] **`feat/metricas`:** endpoint `/metrics` no formato do Prometheus (biblioteca `prometheus_client` ou `prometheus-fastapi-instrumentator`, decidido na aula). Além das métricas HTTP (requisições, latência, status por rota), as do domínio:
  - histograma de latência do LLM e da busca vetorial;
  - contador de perguntas por resultado (respondida, recusada pelo limiar, erro);
  - contador de tokens de entrada e saída, vindo do `usage` da etapa 9 (é daí que sai o gasto estimado).
- [ ] O `/metrics` fica só na rede interna: o nginx do `web` **não** repassa essa rota.
- [ ] Teste na suíte: depois de um `/ask` com o LLM falso, o `/metrics` mostra o contador incrementado.

*Pronto quando:* `curl localhost:8000/metrics` mostra as métricas do domínio e o teste está na CI.
*Para estudar:* os 4 tipos de métrica (counter, gauge, histogram, summary), cardinalidade de *labels*, RED e USE.

### Etapa 13 — Prometheus e Grafana no ar

- [ ] **`feat/observabilidade`:** Prometheus, Grafana e node_exporter no compose (local e prod), com retenção curta (`--storage.tsdb.retention.time`) para caber no disco.
- [ ] Grafana **provisionado como código** (pasta versionada com a fonte de dados e os painéis em JSON): subir do zero já mostra tudo, sem clique. Senha do admin vinda do Parameter Store, nunca o `admin/admin` padrão.
- [ ] Painéis: taxa, erros e latência da API; latência do LLM (p50/p95 contra o timeout); tokens e gasto estimado por dia; CPU, RAM e disco do EC2.
- [ ] Grafana e Prometheus sem porta pública: acesso pelo túnel do SSM, como a interface.

*Pronto quando:* o painel do EC2 mostra perguntas reais e o gasto estimado bate (aproximadamente) com o Console da Anthropic.
*Para estudar:* *pull* × *push*, PromQL (`rate`, `histogram_quantile`), *recording rules*.

### Etapa 14 — Alertas

- [ ] Regras de alerta versionadas: API fora do ar, taxa de erro alta, p95 do LLM perto do timeout, gasto estimado do dia acima de um limite seu.
- [ ] Destino da notificação (e-mail, Telegram ou Discord: decidido na aula), pelo Alertmanager ou pelo alerting do Grafana.
- [ ] **Portão na CI:** `promtool check rules` e `promtool test rules` com casos de teste das regras.

*Teste de bloqueio:* `docker compose stop api` no EC2 → o alerta dispara e a notificação chega; `start` → ele se resolve.
*Pronto quando:* você recebe o alerta de uma queda provocada e o PR com uma regra quebrada é barrado.

---

## Bloco G — Encerramento

### Etapa 15 — Evidências e `terraform destroy`

- [ ] Guardar antes de destruir: prints dos painéis, do alerta recebido, do deploy automático e do rollback, e os links dos PRs barrados.
- [ ] `terraform destroy` e conferência: nenhuma instância, volume, IP público ou snapshot sobrando no Cost Explorer depois de uns dias.
- [ ] Revogar a chave `edurag-prod` no Console da Anthropic, apagar os parâmetros do SSM e a *role* do OIDC (se ficou fora do Terraform), e por último o bucket do *state*.

*Pronto quando:* a fatura do mês seguinte vem zerada e a evidência está no README.

---

## Fora do caminho

Saíram em 12/11/2026, porque o ambiente é privado e temporário. Voltam se o projeto um dia ficar público:

- Autenticação de usuários (Basic no nginx, API key ou JWT), cota diária por usuário, teto no `top_k`, `limit_req` no nginx, CORS e cabeçalhos de segurança. A análise de risco está na aula 0009 e na referência [Exposição segura](estudo/reference/exposicao-segura.html).
- Domínio e HTTPS públicos.

## Depois da trilha

- **F5 — LLMOps:** Langfuse, Ragas na CI (vira mais um portão da pipeline), defesa contra prompt injection e experimento de `CHUNK_SIZE`.
- **F6 — Kubernetes.**
- Logs centralizados (Loki) e tracing (OpenTelemetry), a outra metade da F4.

## Comprovação para o currículo

Guarde, a cada etapa, o print ou o link do PR que provou o portão: o PR com segredo falso barrado, o PR com dependência vulnerável barrado, o PR com porta aberta barrado pelo portão de IaC, o deploy automático, o rollback e o alerta recebido. Junto com o README, isso vira a evidência de "DevSecOps na prática".
