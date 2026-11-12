# Etapa 8 concluída: cada merge na main vira uma imagem no GHCR

Os jobs `publica-api` e `publica-front` do `build.yml` rodam só em push na `main` (`if: github.event_name == 'push' && github.ref == 'refs/heads/main'`), dependem do portão da mesma imagem (`needs: imagem-api` / `needs: imagem-front`) e são os únicos com `packages: write`. O login é feito com o `GITHUB_TOKEN`, sem nenhum segredo novo. Cada imagem recebe duas tags: o SHA completo do commit e `latest`, só como apelido. Entrou no [PR #40](https://github.com/rafelms/EduRAG/pull/40), mesclado em 04/11/2026. Ele escreveu o YAML sem esqueleto e sem co-autoria da IA no commit `b6a089c`.

**Evidence:**
- Run de PR ([43167551617](https://github.com/rafelms/EduRAG/actions/runs/43167551617), do #46): `imagem-api` e `imagem-front` passaram; `publica-api` e `publica-front` ficaram como `skipped`. Ou seja, PR não publica.
- Run na `main` ([43167826445](https://github.com/rafelms/EduRAG/actions/runs/43167826445), merge do #46): os 4 jobs com `success`.
- No GHCR, `edurag-api` tem uma tag por merge desde o #40: `7f06c71…` (04/11), `f447044…`, `cf04e38…` e `cd809cb…` (12/11). `latest` está só na `cd809cb…`, a mais recente.
- Os dois pacotes são **públicos**: `docker buildx imagetools inspect` funciona sem nenhuma credencial do `ghcr.io`.

**Insights:**
- Cada push cria **3 versões** no GHCR, e só uma tem tag. Ela é um *image index* (OCI) com dois manifests dentro: a imagem `linux/amd64` e um `attestation-manifest` (proveniência, que a `build-push-action` gera por padrão quando faz push). As versões sem tag não são lixo: apagar uma delas quebra o pull da tag.
- Na tag `cd809cb…` da `api`, apareceram só 2 versões novas. O manifest amd64 (`sha256:6d5b00d6…`) é **o mesmo** do push do `cf04e38`: o #46 só mexeu no front, e o rebuild da `api` com o cache `gha` deu uma imagem idêntica, byte a byte.
- Isso responde em parte a uma dúvida do desenho. O `publica-*` não envia a imagem escaneada: ele refaz o build. Com as mesmas entradas e o cache, o digest sai igual. Mas isso não é garantido: se o cache falhar, ou se a tag da base mudar entre os dois jobs, a imagem publicada não é a escaneada.
- O `needs` liga a publicação só ao portão de imagem do mesmo workflow. Os portões de código (`gitleaks`, `semgrep`, `trivy-fs`) rodam em paralelo no push da `main`. Isso é aceitável porque o ruleset já exigiu esses checks no PR antes do merge.
- As `env` `DOCKER_BUILD_RECORD_UPLOAD`/`DOCKER_BUILD_SUMMARY` ficaram só nos jobs `publica-*`; os `imagem-*` continuam sem elas.

**Implicações:**
- Rollback = subir a tag do SHA anterior. É o que a etapa 11 vai usar; `latest` não serve para isso.
- Pacotes públicos: o EC2 consegue puxar sem credencial. Na etapa 10, decidir se o ECR ainda é necessário ou se o GHCR basta.
- A melhoria possível no desenho é publicar **o mesmo digest** que foi escaneado: `push` por digest no job do portão, ou `docker save` + artefato entre os jobs. Fica registrado, sem pressa.
- Retenção: são 3 versões por merge, inclusive nos merges só de docs e do Dependabot. Mais adiante, definir uma política de limpeza: manter as últimas N tags de SHA e apagar cada *index* antigo **junto com os manifests filhos dele**, nunca um filho sozinho.
