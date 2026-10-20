# Semgrep como portão de SAST, provado

Ele colocou o job `semgrep` no `security.yml` (relatório em SARIF → envio → portão com `--severity ERROR --error`), adicionou `semgrep` aos checks obrigatórios do `protege-main` e provou o bloqueio no PR #10. Entendeu que o rótulo "Blocking" do Semgrep não bloqueia nada sozinho: quem bloqueia é o código de saída, que deixa o step e o job vermelhos, mais o check obrigatório. Também entendeu por que só o `semgrep` vai no ruleset, e não o check `Semgrep OSS` da code scanning.

**Evidence:** PR #10 em 20/10/2026: `semgrep` (Required) com *failure* por `avoid-sqlalchemy-text` na linha 7 de `app/teste_sast.py`; `backend`, `frontend` e `gitleaks` com *success*; merge bloqueado. O check `Code scanning results / Semgrep OSS` também falhou, sem ser obrigatório.

**Tropeços:**
- Criou a branch `ci/semgrep`, mas commitou na `main` local, porque não fez o `switch`. É o mesmo modelo mental frágil da etapa 3 ("o commit vai para a branch em que eu estou"). Ele corrigiu com `merge --ff-only` e `reset --hard origin/main`.
- O primeiro `security.yml` repetiu `permissions` e `steps` dentro do job `gitleaks` e usou `id: semgrep` no lugar de uma chave de job. A estrutura YAML de jobs e steps ainda não está firme. Ele pediu o arquivo corrigido e eu escrevi; o combinado era só apontar as linhas.
- Erro do professor: a aula dizia que o arquivo da prova passava no ruff, mas eu tinha testado sem o `pyproject.toml` (regras `ANN`). A primeira versão da prova derrubou também o `backend`. Corrigido na aula.

**Insights dele:** perguntou se a prova deveria ficar em `tests/`. Isso levou à descoberta de que o Semgrep ignora `tests/` por padrão (os 11 arquivos do `Scan skipped`). Também fez perguntas de mercado: o Semgrep em Spring Boot e PRs com CI verde que mesmo assim são recusados.

**Implicações:**
- Etapa 6: os 11 avisos (10 tags de action e 1 cooldown do uv) são a lista de tarefas. Depois de zerados, discutir tirar o `--severity ERROR` do portão.
- Antes de mais um portão, treinar a estrutura YAML sem ajuda, por exemplo reescrevendo o job `semgrep` de memória.
- Reforçar `git switch -c` e conferir o `*` antes de commitar.
- Etapa 11: retomar entrega contínua × deploy contínuo e *environments* com aprovação, já que ele chegou a esse tema sozinho.
