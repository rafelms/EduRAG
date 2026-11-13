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

- [Trivy: Filesystem](https://trivy.dev/latest/docs/target/filesystem/)
  O `trivy fs`: o que varre por padrão (vulnerabilidades e segredos), como acha os lockfiles. Usar para: etapa 6.
- [README da trivy-action](https://github.com/aquasecurity/trivy-action)
  Entradas da action (`scan-type`, `severity`, `exit-code`, `ignore-unfixed`, `scanners`, `version`). Os nomes foram conferidos no `action.yaml` da `v0.35.0`. Usar para: escrever o job `trivy-fs`.
- [Aqua: Trivy supply chain attack, what you need to know](https://www.aquasec.com/blog/trivy-supply-chain-attack-what-you-need-to-know)
  O incidente de 19/03/2026: 76 de 77 tags da `trivy-action` movidas para código malicioso, o que o código roubava e a recomendação de fixar por SHA. Usar para: o porquê do SHA (aulas 0004 e 0005).
- [npm: npm-audit](https://docs.npmjs.com/cli/v11/commands/npm-audit)
  `--audit-level`, `--omit=dev`, códigos de saída e o que o comando envia ao registro. Usar para: job `npm-audit`.
- [GitHub: Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
  Fixar actions por SHA, o que conferir (fork), e o limite: o Dependabot não alerta sobre actions fixadas por SHA. Usar para: etapa 6.
- [GitHub: Dependabot options reference](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference)
  Campos do `dependabot.yml`, valores de `package-ecosystem`, `cooldown`, `groups`. Usar para: PR 5 da etapa 6.
- [uv: Settings, `exclude-newer`](https://docs.astral.sh/uv/reference/settings/#exclude-newer)
  Corte por data ou duração relativa (`"7 days"`) e `exclude-newer-package`. Usar para: cooldown do uv.
- [PyPI: análise do ataque à `ultralytics`](https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/)
  Quatro versões maliciosas publicadas pela pipeline do próprio projeto, comprometida via cache do GitHub Actions, depois removidas. Não diz quanto tempo ficaram no ar. Usar para: o porquê do cooldown (aula 0007).
- [OSV](https://osv.dev)
  Banco aberto de vulnerabilidades com API (`POST /v1/query`). Usar para: conferir se uma versão que o cooldown segura é correção de segurança.

- [README da build-push-action](https://github.com/docker/build-push-action)
  Entradas `context`, `file`, `push`, `load`, `tags`, `cache-from`, `cache-to`. `load` é atalho para `--output=type=docker`. Usar para: etapa 7.
- [README da setup-buildx-action](https://github.com/docker/setup-buildx-action)
  O driver padrão é o `docker-container`, que permite exportar cache. Usar para: etapa 7.
- [Docker: GitHub Actions cache backend](https://docs.docker.com/build/cache/backends/gha/)
  `type=gha`, `mode`, `scope` (um por imagem), cache só da branch atual, da base e da padrão, e a API v2 do cache. Usar para: cache do build.
- [Trivy: Container Image](https://trivy.dev/latest/docs/target/container_image/)
  `trivy image`: pacotes do SO e de linguagem, imagem local antes do registro, `--input` para `docker save`. Usar para: etapa 7.

- [GitHub: Publishing Docker images](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images)
  Exemplo oficial para o GHCR: `packages: write`, `docker/login-action` com `github.actor` e `GITHUB_TOKEN`, `metadata-action`, `attest`. Usar para: etapa 8.
- [GitHub: Working with the Container registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
  Pacote nasce privado; vínculo automático com o repositório quando publicado por workflow; `GITHUB_TOKEN` × token pessoal. Usar para: etapa 8.

- [OWASP API Security Top 10 (2023)](https://api-security.owasp.org/editions/2023/en/0x11-t10/) e a [API4: Unrestricted Resource Consumption](https://api-security.owasp.org/editions/2023/en/0xa4-unrestricted-resource-consumption)
  A lista de riscos de API e o porquê da etapa 9: serviço pago por requisição, rate limiting, teto em todo parâmetro de entrada, limites de gasto nos provedores. Usar para: modelo de ameaça (aula 0009). Os controles de exposição pública (antigas aulas 0011 a 0013) saíram do caminho em 12/11/2026.
- [Anthropic: Rate limits](https://platform.claude.com/docs/en/api/rate-limits)
  Teto de gastos por tier e o seu próprio, os erros ao estourar (`429 enforced_spend_limit_reached` × `400 invalid_request_error`), limites por workspace. Usar para: aulas 0009 e 0010.
- [Anthropic: Workspaces](https://platform.claude.com/docs/en/manage-claude/workspaces)
  Chave presa ao workspace; Default Workspace sem teto de gastos; onde ficam o teto e a taxa do workspace no Console. Usar para: aula 0009.
- [Anthropic: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
  A Anthropic não tem modelo de embeddings; indica a Voyage AI (dimensões, `input_type`). Usar para: decisão dos embeddings (aula 0010).
- [Vite: Env Variables and Modes](https://vite.dev/guide/env-and-mode)
  `VITE_*` vai para o JavaScript público e não deve ter chave de API. Usar para: o porquê de a chave morar só na API.
- [nginx: ngx_http_limit_req_module](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)
  `limit_req_zone`, `burst`, `nodelay`, `limit_req_status` (padrão `503`). Usar para: aula 0012.
- [FastAPI: Security](https://fastapi.tiangolo.com/tutorial/security/) e o tutorial [OAuth2 com JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
  As ferramentas de `fastapi.security` e o fluxo de login com hash de senha. Usar para: aula 0011.

### AWS e Terraform (etapa 10)

- [Terraform: State](https://developer.hashicorp.com/terraform/language/state)
  Para que serve o *state*, o `terraform.tfstate` local e por que usar um backend remoto. Usar para: aulas 0011 e 0012.
- [Terraform: Manage sensitive data](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)
  O *state* e o *plan* guardam segredos em texto puro; valores *ephemeral* e argumentos *write-only*. Usar para: o porquê do `aws ssm put-parameter` à mão.
- [Terraform: Backend S3](https://developer.hashicorp.com/terraform/language/backend/s3)
  `bucket`, `key`, `region`, `use_lockfile` (trava `.tflock` no S3), `encrypt`, permissões mínimas no bucket; trava pelo DynamoDB obsoleta; versionamento recomendado. Usar para: aula 0012.
- [Terraform: Install](https://developer.hashicorp.com/terraform/install) e [releases](https://releases.hashicorp.com/terraform/)
  Zip para Windows (AMD64) com `SHA256SUMS`; sem winget ou Chocolatey na página oficial. Última estável em 13/11/2026: 1.17.2. Usar para: instalar e atualizar.
- [Registry: hashicorp/aws](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
  Documentação de cada recurso e a versão atual (6.73.0 em 11/11/2026). Usar para: aulas 0012 a 0014, forma de cada recurso.
- [AWS Sign-In: Sign in through the AWS CLI](https://docs.aws.amazon.com/signin/latest/userguide/command-line-sign-in.html)
  `aws login` (CLI ≥ 2.32.0, até 12 h, `SignInLocalDevelopmentAccess`, `--profile`, `aws logout`) e o `aws sso login`. Usar para: credencial local sem access key.
- [IAM: Root user best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html)
  MFA no root, sem access key do root, root só para tarefa de root. Usar para: aula 0011.
- [Enable IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/enable-identity-center.html)
  Instância de organização × de conta; numa conta do plano gratuito, criar a Organization passa a conta para o pago e os créditos expiram. Usar para: o porquê de usar IAM com `aws login`.
- [EC2: Track your Free Tier usage](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html) e [AWS Free Tier](https://aws.amazon.com/free/)
  Tipos elegíveis para contas a partir de 15/07/2025, créditos, 6 meses, comando `describe-instance-types` com o filtro `free-tier-eligible`. Usar para: escolher a instância (aula 0013).
- [Supported services for Sign up for AWS (new)](https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html)
  Serviços liberados na experiência nova com *projects* (EC2, S3, SSM, IAM, Budgets sim; Identity Center e Organizations não). Usar para: se a conta foi criada por esse caminho.
- [AWS Budgets: Create a budget](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-create.html) e [Budgets pricing](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/)
  Modelo simplificado × personalizado; monitorar e notificar é grátis, ações de budget têm cota grátis. Usar para: aulas 0011 e 0014 (`import`).
- [EC2: How stop and start works](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/how-ec2-instance-stop-start-works.html)
  Parada não cobra uso, o EBS continua cobrando, o IPv4 automático é devolvido no `stop`. Usar para: rotina de desligar.
- [VPC pricing](https://aws.amazon.com/vpc/pricing/) e [EBS pricing](https://aws.amazon.com/ebs/pricing/)
  IPv4 público a US$ 0,005/h; gp3 com 3.000 IOPS e 125 MB/s incluídos. Usar para: tabela de custos.
- [Vantage: t3.medium](https://instances.vantage.sh/aws/ec2/t3.medium?region=us-east-1)
  Preço por hora quando a tabela oficial da AWS não carrega em texto (US$ 0,0416/h em 13/11/2026). Fonte não oficial: confirme na [Calculator](https://calculator.aws/).
- [Systems Manager pricing](https://aws.amazon.com/systems-manager/pricing/)
  Session Manager grátis em EC2; parâmetros padrão do Parameter Store grátis. Usar para: aulas 0013 e 0014.
- [Session Manager plugin no Windows](https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-windows.html) e [verificação](https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-verify.html)
  Instalador `.exe`, pasta padrão, só PowerShell e cmd, mensagem esperada. Usar para: aula 0011.
- [AWS CLI: Install](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
  `msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi` e `aws --version`. Usar para: aula 0011.
- [Classmethod: Terraform S3 backend com aws login](https://dev.classmethod.jp/articles/terraform-s3-backend-aws-login/) e a [issue #45316](https://github.com/hashicorp/terraform-provider-aws/issues/45316)
  Testou: provider ≥ 6.23.0 e Terraform ≥ 1.15.0 leem o `login_session`. Fonte não oficial. Usar para: se o `init` não achar credencial.

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
- Como o Dependabot (`github-actions`) lê o `directory`, e se ele atualiza o comentário `# vX.Y.Z` de um SHA: a referência que li foi truncada nesse ponto. A frase sobre o comentário vem do guia de uso seguro, não da referência do Dependabot.
- A partir de qual versão o uv entende `exclude-newer = "7 days"`: a documentação não diz. Observado: o uv 0.5 falha; o 0.9 e o 0.13.1 leem o arquivo.
- Se `v0.76.1` do Trivy é segura: não achei aviso contra, mas a Aqua só nomeia como seguras a `0.69.2` e a `0.69.3` (para o incidente de março). Observado: a imagem oficial `0.76.1` rodou limpa.
- O nome exato do check obrigatório de um job com *matrix* (a aula 0006 manda ele conferir na lista do ruleset, não testei). A documentação do Docker que li também não define `mode=min` e `mode=max` do cache `gha`.
- Se o limite de 10 GB do cache do GitHub afeta o EduRAG: a página do Docker que li não menciona o limite.
- Se um job pulado por `if` conta como sucesso num check obrigatório: não conferi. A aula 0008 evita a dúvida mantendo os `publica-*` fora do ruleset.
- A página do Container registry diz que imagens públicas podem ser baixadas anonimamente, mas também que é preciso token para "instalar" pacotes públicos. Testar o `docker pull` sem login na etapa 8.
- A página de Rate limits da Anthropic não diz se os alertas de gasto do workspace chegam por e-mail nem a quem. Conferir na tela, na aula 0009.
- A estimativa de custo por pergunta (aula 0009) não inclui os tokens de raciocínio do modelo: medir com o `usage` real na aula 0010.
- Se o AWS Budgets conta o gasto **antes** ou **depois** dos créditos do plano gratuito. Com créditos, um alerta de custo pode nunca disparar. Conferir nas opções do budget (aula 0011).
- Se o plano gratuito **recusa** lançar um tipo não elegível (como o `t3.medium`) ou só cobra dos créditos. A página diz "You can't exceed your Free Tier limits", sem detalhar. Conferir na aula 0013.
- Documentação oficial da HashiCorp sobre a versão mínima do Terraform e do provider que leem o `aws login`: só achei fonte de terceiros.
- Os preços exatos de gp3 e S3 Standard em `us-east-1`: as páginas oficiais carregam a tabela por script. Conferir na Calculator.
- [GitHub Status](https://www.githubstatus.com): primeiro lugar a olhar quando os checks ficam presos em *Queued* sem log (foi um incidente do Actions no PR #6).
