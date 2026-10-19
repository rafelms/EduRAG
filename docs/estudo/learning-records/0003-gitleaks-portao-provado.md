# Gitleaks como portão de segredos, provado

Ele criou o `security.yml` com o job `gitleaks`, colocou o job nos checks obrigatórios do `protege-main`, rodou a varredura do histórico (nenhum achado) e provou o bloqueio no PR #6. A chave AWS falsa aleatória foi detectada (`aws-access-token`), o bot comentou na linha e o merge ficou bloqueado. Ele também entendeu por que o gitleaks não "verifica" a chave: são palavras-chave, regex, entropia e exceções, tudo offline.

**Evidence:** PR #6 em 19/10/2026: `gitleaks` com *failure*, `backend` com *success*, merge bloqueado. A varredura local terminou com saída 0.

**Tropeços:**
- O primeiro `security.yml` tinha erros de estrutura YAML: `with` solto no job, `name` fora do item da lista de steps, `variables` no lugar de `env` e faltava o checkout. O modelo "a indentação e o `-` dizem a quem cada chave pertence" ainda não está firme. Ele pediu a correção; na próxima etapa, ele mesmo deve corrigir a partir dos apontamentos.
- Errou no quiz por que o job precisa de `fetch-depth: 0` (clone raso: sem o pai do primeiro commit do PR, o intervalo `D^..D` não existe). Retomar com recuperação espaçada.
- Os checks ficaram presos em *Queued* por um incidente do GitHub Actions. Ele achou que o bot tinha travado a CI. Aprendeu a olhar o githubstatus.com e a distinguir "job vermelho com log" (erro dele) de "fila sem log" (plataforma).

**Implicações:** na etapa 5, reforçar a estrutura de steps (`uses` + `with` no mesmo item) e perguntar de novo se o Semgrep precisa de `fetch-depth: 0`. O fluxo branch → PR → merge → pull está ficando natural (PRs #4, #5 e #6 seguiram o fluxo certo).
