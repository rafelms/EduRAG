# Notas do professor

- Material de estudo fica em `docs/estudo/`, nunca na raiz do repositório.
- O Rafael quer **fazer na mão**: as aulas dão o porquê e o roteiro; ele configura e escreve. A IA não aplica a configuração por ele.
- Ele estranha chamadas a ferramentas sem explicação: dizer antes para que serve cada pesquisa.
- Idioma: português. Estilo das docs dele: direto, com tabelas, sem enrolação.
- Anotações anteriores dele: [estudo-ci.md](../estudo-ci.md) (etapas 1 e 2).
- Repositório público (`rafelms/EduRAG`), plano gratuito. Checks obrigatórios: `backend`, `frontend` (workflow `CI`) e `gitleaks` (workflow `Security`).
- Máquina: Fedora (SELinux). Volumes Docker precisam de `:Z`.
- Workflows de segurança do Bloco B vão em `.github/workflows/security.yml`, separados do `ci.yml`.
- Há um glossário em `reference/glossario.html`: usar os mesmos termos em toda aula e acrescentar os novos.
- 19/10/2026: errou a questão 4 da aula 0002 (`fetch-depth: 0`). Explicado com clone raso + intervalo `D^..D`. Retomar na próxima aula como recuperação espaçada (ex.: o Semgrep precisa de `fetch-depth: 0`?).
- 19/10/2026: etapa 4 concluída e provada (PR #6). O primeiro `security.yml` dele tinha erros de estrutura YAML (`with` fora de step, `name` fora do item da lista, `variables` no lugar de `env`, sem checkout). Ele pediu que eu corrigisse e eu corrigi, explicando cada erro. Na próxima, só apontar as linhas e deixar a correção com ele.
- Ele não tem o `gh` instalado; para checar runs e checks, uso a API pública do GitHub com `curl`.
- 20/10/2026: aula 0003 criada (etapa 5). Testei antes com Semgrep 1.180.0: `p/default` no repo dá 8 achados, todos de cadeia de suprimentos (7 tags de action, 1 cooldown do uv), nenhum no código da app. Desenho escolhido: SARIF com tudo, portão só com `--severity ERROR`. O `p/python` **não** pega `execute("..." + x)`; o `p/default` pega. A prova usa `text(sql_concatenado)` em `app/teste_sast.py` (ruff passa). Na revisão do YAML, **só apontar as linhas**; ele corrige.
- 20/10/2026: etapa 5 provada (PR #10). Ver learning record 0004. Ele pediu o `security.yml` corrigido e eu escrevi; da próxima vez, oferecer primeiro só os apontamentos.
- **Testar as provas sempre com a config do projeto** (`uv run ruff check`, que lê o `pyproject.toml`), nunca com `uvx ruff` solto: errei isso na 0003.
- Ele faz perguntas de mercado ("e no Spring Boot?", "PR verde recusado?"). Responder com tabela curta e apontar uma comunidade (r/devops, r/brdev).
- Próximo: aula 0004, etapa 6 (dependências: Dependabot, `trivy fs`, `npm audit`, actions por SHA, cooldown do uv). Os 11 avisos do Semgrep são a lista de tarefas dela.
