# Recursos: DevSecOps com GitHub Actions e AWS

## Conhecimento

- [Docs do GitHub: About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
  O que é um ruleset e como ele difere da proteção de branch clássica (vários rulesets se somam, dá para desativar sem apagar). Usar para: etapa 3.
- [Docs do GitHub: Creating rulesets for a repository](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)
  O passo a passo na interface. Usar para: criar ou editar o ruleset da `main`.
- [Docs do GitHub: Available rules for rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
  O que cada regra faz (bloquear exclusão, bloquear force push, exigir PR, exigir checks, modo estrito). Usar para: escolher regras em qualquer portão.
- [Docs do GitHub: Remediating a leaked secret](https://docs.github.com/en/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/remediating-a-leaked-secret)
  Por que apagar num commit novo não resolve e por que revogar vem primeiro. Usar para: etapa 4 e qualquer vazamento real.
- [README do gitleaks](https://github.com/gitleaks/gitleaks)
  Comandos da v8 (`git`, `dir`, `stdin`), flags, `.gitleaksignore`, `gitleaks:allow`, códigos de saída. Aviso: o projeto está *feature complete* e só recebe correções de segurança; o autor migrou para o Betterleaks. Usar para: etapa 4.
- [README da gitleaks-action](https://github.com/gitleaks/gitleaks-action) e o [código dela](https://github.com/gitleaks/gitleaks-action/blob/master/src/gitleaks.js)
  Variáveis da action, licença (só para organizações) e quais commits ela analisa em PR e em push. Usar para: escrever e depurar o job.
- [Regras padrão do gitleaks (`gitleaks.toml`)](https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml)
  A regex e as exceções de cada regra. Foi aqui que apareceu a exceção `.+EXAMPLE$` da regra da AWS. Usar para: entender por que algo foi ou não foi detectado.
- [Docs do GitHub: About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
  A versão clássica. Explica que, por padrão, as regras não valem para administradores e que os nomes dos jobs precisam ser únicos entre workflows.
- [Docs do GitHub: Approving a pull request with required reviews](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/approving-a-pull-request-with-required-reviews)
  Fonte da regra "o autor não aprova o próprio PR". Usar para: decidir quantas aprovações exigir num projeto solo.

- [OWASP: Source Code Analysis Tools](https://community.owasp.org/Source_Code_Analysis_Tools) e [Vulnerability Scanning Tools](https://community.owasp.org/Vulnerability_Scanning_Tools)
  Definições de SAST e DAST, com pontos fortes e fracos (falsos positivos, não vê configuração). Usar para: etapa 5, o porquê.
- [Semgrep: CLI reference](https://docs.semgrep.dev/cli-reference)
  Flags do `semgrep scan` (`--config`, `--sarif-output`, `--severity`, `--error`, `--metrics`) e códigos de saída. Usar para: escrever o job.
- [Semgrep: Sample CI configs](https://docs.semgrep.dev/semgrep-ci/sample-ci-configs)
  O `semgrep ci` exige `SEMGREP_APP_TOKEN`; sem conta, é `semgrep scan`. Usar para: entender por que não usamos o exemplo padrão.
- [Semgrep: Ignoring files, folders, and code](https://docs.semgrep.dev/ignoring-files-folders-code)
  `# nosemgrep: id` e `.semgrepignore`. Usar para: falso positivo.
- [Regras do Semgrep (`semgrep-rules`)](https://github.com/semgrep/semgrep-rules)
  O YAML de cada regra, com CWE e a correção recomendada. Usar para: entender por que algo foi ou não foi apontado.
- [Docs do GitHub: Uploading a SARIF file](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github)
  `upload-sarif@v4`, `security-events: write` e `category`. Usar para: etapa 5 e qualquer ferramenta que gere SARIF (Trivy na etapa 7).

## Sabedoria (comunidades)

- [GitHub Community: discussões de Actions](https://github.com/orgs/community/discussions/categories/actions)
  Fórum oficial, com funcionários do GitHub respondendo. Usar para: checks que não aparecem, workflows que não disparam.
- [r/devops](https://www.reddit.com/r/devops/)
  Comunidade grande de profissionais. Usar para: pedir crítica da pipeline quando ela estiver pronta.

## Lacunas

- Fonte oficial sobre o limite de tempo para um check aparecer na lista de checks obrigatórios.
- Qual versão do gitleaks a `gitleaks-action@v3.0.0` usa por padrão (não está documentada; por isso fixamos `GITLEAKS_VERSION`).
- ~~Se o *push protection* do GitHub barra um ID de chave da AWS sozinho.~~ Observado em 19/10/2026: **não barra** (o push do PR #6 passou); só o gitleaks pegou. Ainda sem fonte oficial.
- Se a imagem `semgrep/semgrep` (Alpine) roda actions JavaScript como o `upload-sarif` dentro de um job `container:`. Não achei fonte oficial; por isso a aula 0003 roda o Semgrep pelo `uvx` no runner normal.
- [GitHub Status](https://www.githubstatus.com): primeiro lugar a olhar quando os checks ficam presos em *Queued* sem log (foi um incidente do Actions no PR #6).
