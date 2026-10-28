# Primeira rodada do Dependabot: 8 PRs mesclados com a regra `strict`

O `dependabot.yml` (PR #18) abriu 8 PRs em 27/10/2026: 5 de frontend (#19 a #23) e 3 de backend (#24 a #26). Todos os merges foram feitos pela interface do GitHub em 28/10, um de cada vez, do menor risco para o maior. A cada merge, o PR seguinte foi atualizado com `@dependabot rebase` (ou pelo rebase automático do bot, quando havia conflito) e só foi mesclado depois de ficar verde de novo.

**Evidence:** primeiro merge de PR do Dependabot no [PR #25](https://github.com/rafelms/EduRAG/pull/25) (13:38); o último foi o #22 (15:29). CI e Security verdes na `main` em `9f63ff9`. *Insights → Dependency graph → Dependabot* com os 4 blocos (uv, npm, docker, github-actions) lidos sem erro.

**Tropeços:**
- O #20 (`node:26-alpine`) e o #23 (`@types/node` 26) entraram, embora o combinado fosse esperar a Node 26 virar LTS. A imagem passou a construir com a Node 26 enquanto o job `frontend` testava com a 24. A CI foi alinhada no PR #27. Fica a lição: PR de Docker verde não prova nada até a etapa 7, porque nenhum check olha o `Dockerfile`.
- No #24 apareceu a tela de resolução de conflito do GitHub. O Dependabot já tinha refeito o PR três minutos depois do merge do #26, e o certo era fechar a tela sem resolver nada.

**Insights:**
- A regra `strict` do `protege-main` exige que o branch esteja atualizado com a `main`. Cada PR passou sozinho, mas isso não prova que eles funcionem juntos. Daí o "out of date" depois de cada merge.
- O Dependabot só faz rebase sozinho quando há **conflito de texto** (o #24 brigou com o #26 em linhas vizinhas do `pyproject.toml` e do `uv.lock`). Branch só desatualizado pede `@dependabot rebase`. O botão "Update branch" cria um commit de outra pessoa no branch, e com isso o bot para de cuidar do PR.
- O número do PR é a ordem de criação, não a de merge. Qualquer ordem funciona com o ciclo rebase → CI → merge. Começar pelo menor risco serve para saber na hora quem quebrou.
- `Semgrep OSS` (check do code scanning, não obrigatório) pode travar em `queued` depois do upload do SARIF. Quem barra o PR é o job `semgrep`, e ele tinha passado.
- O `python:3.12-slim` da raiz foi lido, mas não gerou PR: as tags `3.13-slim` a `3.15-slim` caíram no cooldown padrão de 3 dias do Dependabot. O `COPY --from=ghcr.io/astral-sh/uv:0.5` não é acompanhado pelo Dependabot.

**Implicações:**
- O cooldown do uv só pode entrar a partir de 30/10: o #24 subiu o mínimo do `fastapi` para a 0.162.0 (23/10), e um mínimo mais novo que o prazo faz o `uv lock` falhar, não só rebaixar. No mesmo PR vai o `cooldown` no bloco `uv` do `dependabot.yml`, para os dois respeitarem o mesmo prazo, e o uv do `Dockerfile` atualizado à mão.
- Repositório de conta pessoal não tem merge queue. O ciclo manual continua, ou com auto-merge (hoje desligado nas configurações).
