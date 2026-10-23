# Trivy e npm audit como portões de dependências, provados

Ele corrigiu o `certifi` (PR #12), criou os jobs `trivy-fs` e `npm-audit` no `security.yml` (PR #13), colocou os dois nos checks obrigatórios do `protege-main` e provou o bloqueio no PR #14, com `pyyaml==5.3` (Python) e `lodash@4.17.20` (npm). Entendeu que SCA muda com o tempo: reparou sozinho que a severidade e os avisos do log dele diferiam do meu teste, e a explicação é o banco de vulnerabilidades crescer. Também aprendeu a fixar uma action por SHA: a `trivy-action` ficou no commit da linha `^{}`.

**Evidence:** PR #14 em 23/10/2026, fechado sem merge. `trivy-fs` com *failure* (`uv.lock`: `pyyaml 5.3` com 2 CRITICAL, `CVE-2020-14343` e `CVE-2020-1747`; `package-lock.json`: `lodash` com 2 HIGH, `CVE-2021-23337` e `CVE-2026-4800`), `npm-audit` com *failure* (`lodash`), `backend`, `frontend` e `gitleaks` com *success*, `trivy-fs` e `npm-audit` com o selo *Required* e o botão de merge desabilitado. Jobs: [`trivy-fs`](https://github.com/rafelms/EduRAG/actions/runs/39982005609/job/120511410590) e [`npm-audit`](https://github.com/rafelms/EduRAG/actions/runs/39982005609/job/120511411002).

**Tropeços:**
- O primeiro `security.yml` desta etapa misturou os jobs: `trivy-fs` com `uvx trivy@0.44.0` (o Trivy não está no PyPI), uma chave `default: work` que não existe, `npm-audit` copiado do `trivy-fs` (rodava Trivy, não `npm audit`) e o step *Enviar SARIF* do `semgrep` apagado sem querer, o que tiraria os achados do Semgrep da aba Security. Ele pediu a correção e eu escrevi o arquivo, de novo, apesar do combinado de só apontar as linhas. A estrutura YAML de jobs e steps continua sendo o ponto mais frágil, pela terceira etapa seguida.
- Disse que não entendeu como "configurar o SHA". Só um exemplo passo a passo (`ls-remote` → copiar o SHA → `uses: repo@sha # versão`) destravou; depois acertou a pegadinha da tag anotada sozinho.
- Fez o commit do PR 2 antes de separar do PR 1 e quis desfazer: aprendeu `git reset` (sem `--hard`), que desfaz o commit e mantém o arquivo.
- Esqueceu o `uv lock` depois de editar o `pyproject.toml`: o `backend` caiu por `uv sync --locked` e o Trivy viu o `uv.lock` limpo, então a primeira prova só pegou o npm. O erro também foi da aula, que não avisava isso. Ele refez com o `uv lock` e as duas provas funcionaram.
- Depois de apagar a branch remota, perguntou se precisava restaurar as configs antigas: a branch local de teste continuava ativa, com `pyyaml` e `lodash` no disco. A `main` estava intacta. O modelo "o commit vai para a branch em que eu estou" melhorou (PRs #12 a #14 seguiram o fluxo) mas ainda precisa de conferência do `*`.

**Insights dele:**
- Reparou na diferença entre o meu teste e o dele (2 HIGH em vez de CRITICAL; avisos mais novos) e levou isso a uma pergunta. Foi a observação certa e levou à lição de que um portão de SCA pode ficar vermelho sem commit novo.
- Reparou que o `backend` falhou sem a aula prever, e cobrou isso. Gerou a regra "vermelho pelo motivo errado não é prova".

**Implicações:**
- A etapa 6 está **pela metade**: faltam actions por SHA, cooldown do uv e `dependabot.yml` (aula 0005, PRs 4 e 5). O Semgrep ainda acusa 13 avisos (12 de actions por tag mais o cooldown). Só depois disso começa a etapa 7.
- Na aula 0005, ele já viu um SHA completo; a tarefa nova é aplicá-lo a seis actions diferentes e lidar com as tags de versão maior (`v7`). Incluir o `uv lock` e `docker build` como conferência explícita nos PRs 4 e 5.
- Para a estrutura YAML, o que funcionou foi um exemplo comentado; o que não funcionou foi só apontar linhas. Na etapa 7, dar um esqueleto do job (chaves e indentação, sem os valores) e deixar ele preencher.
- Reforçar `git switch -c` + `git branch` antes de editar, e `git switch main && git pull` depois de fechar um PR de prova.
