# Etapa 7 provada: imagens só passam sem CRITICAL e sem root

O `build.yml` constrói as duas imagens em todo PR (`push: false`, `load: true`, cache `gha` com `scope` próprio), escaneia com `trivy image` (falha em CRITICAL, `ignore-unfixed`) e roda `id -u` dentro de cada imagem (falha se for `0`). Os jobs `imagem-api` e `imagem-front` são checks obrigatórios do `protege-main` desde 30/10/2026. Ele escreveu o YAML a partir do esqueleto da aula 0006, sem correção minha.

**Evidence:**
- Jobs: [PR #32](https://github.com/rafelms/EduRAG/pull/32) (`imagem-api`), [PR #33](https://github.com/rafelms/EduRAG/pull/33) (desliga o build record da `build-push-action`) e [PR #34](https://github.com/rafelms/EduRAG/pull/34) (`imagem-front`), todos em 29/10.
- Prova do não-root, [PR #35](https://github.com/rafelms/EduRAG/pull/35): `USER edurag` comentado → `imagem-api` vermelho no step *Checagem de não-root* (`uid: 0`, exit 1); build e Trivy verdes. Fechado sem merge.
- Prova do scan, [PR #36](https://github.com/rafelms/EduRAG/pull/36): base `nginx-unprivileged:1.21-alpine` → `imagem-front` vermelho no step *Trivy Image (portão)*, Alpine 3.15.4, `Total: 9 (CRITICAL: 9)` (ex.: `curl CVE-2022-32207`). O scan local deu o mesmo número. Fechado sem merge.
- Os dois PRs ficaram `BLOCKED`.

**Insights:**
- O portão pegou um CRITICAL real antes de qualquer prova: o CVE-2026-111497 no `brotli-libs` da base `nginx-unprivileged:1.31-alpine`, corrigido no próprio PR #34 com `apk upgrade --no-cache brotli-libs` entre `USER root` e `USER 101`. Essas linhas não atrapalharam a prova com a base 1.21: o `apk upgrade` funcionou no Alpine 3.15.
- No #35, o `semgrep` também ficou vermelho, com `dockerfile.security.missing-user` (blocking). Não foi falha pelo motivo errado, foi defesa em profundidade: o Semgrep lê o **texto** do Dockerfile, sem build e em segundos; o `id -u` olha a **imagem** construída e pega também o caso em que a base roda como root sem ninguém escrever nada.
- Estudo slim × completa (30/10, Trivy 0.76.1, sem `--ignore-unfixed`): `python:3.12` tem 1,62 GB, 469 pacotes do Debian, 454 HIGH e 16 CRITICAL; `python:3.12-slim` tem 180 MB, 87 pacotes, 44 HIGH e 0 CRITICAL. A imagem é ~9× maior, mas tem ~10,7× mais achados, e só ela tem CRITICAL: o que pesa são as bibliotecas em C (compiladores, cabeçalhos `-dev`, libs de imagem e XML). O ganho da slim é superfície de ataque, não espaço.
- Os 44 HIGH da slim são exatamente os 44 do `api`: todos os HIGH do `api` vêm da base, nenhum do código ou das dependências Python.

**Implicações:**
- A etapa 8 reaproveita este build e o cache: publicar no GHCR só o que passou por aqui.
- Slim reduz, mas não zera. Uma base menor (distroless) fica para depois da pipeline, não para esta etapa.
- Ponto fraco das etapas anteriores (estrutura YAML) não apareceu: com o esqueleto, ele escreveu os dois jobs certos de primeira. Na etapa 8, testar com menos andaime.
