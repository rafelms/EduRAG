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
- Próximo: aula 0003, etapa 5 (SAST com Semgrep e SARIF).
