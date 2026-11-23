# Aula 0013 concluída: EC2 sem porta de entrada, provado de dentro e de fora

A aula 0013 foi feita em 22/11/2026, passo a passo no chat (PR #64). A máquina subiu pelo Terraform, ficou `Online` no SSM, abriu um nginx de teste pelo túnel, mostrou as 1000 portas `filtered` no `nmap` e saiu inteira com o `destroy`. Duas coisas mudam a próxima aula: **o `apply` mostrou um erro que o `plan` não pegou**, e ele pediu que a IA escrevesse o Terraform a partir do `rede.tf`.

**Evidence:**
- RAM medida no Docker Desktop (`LLM_PROVIDER=claude`): web 10, api 126, postgres 25, ollama 332 MiB, soma ~495 MiB. Na tabela vieram junto contêineres de outro projeto (`supabase_*_lotogestor`), descartados da soma.
- Ele rodou o `describe-instance-types` e a lista trouxe o `t8i.small` (x86, 2 GiB), que a aula não tinha. Preço na Pricing API: US$ 0,0250/h contra 0,0208 do `t3.small`. **Escolha dele: `t3.small`**, porque a mesma RAM custa menos e a CPU não é o gargalo.
- No EC2: AL2023, Docker 25.0.14, compose **v5.7.1** (hash `af426722…054064cf` igual na API do GitHub e no `.sha256` publicado), `cloud-init status: done`, **259 MiB usados de 1909**, swap 0, disco 30G com 2.2G usados.
- `plan`: 6 recursos. Primeiro `apply`: 5 criados e a instância falhou com `InvalidAMIID.Malformed`: o provider 6.73.0 chama `DescribeImages` antes de lançar, e essa API não aceita `resolve:ssm:...`. A correção foi trocar por `data "aws_ssm_parameter"` + `insecure_value` (`ami-01e4a7224fcbfe81f`). A aula foi corrigida no mesmo PR.
- Agente do SSM `Online` (3.3.5828.0), status checks `ok`. Página do nginx aberta em `localhost:8080` pelo túnel. `nmap -Pn --top-ports 1000`: **1000 filtered**, nenhuma open, nem a 8080.
- `destroy`: 6 destruídos, instância `terminated`, nenhum volume solto, state vazio.

**Insights:**
- **Aquecimento:** acertou o `plan`. Não lembrou onde fica o `.tflock` (no bucket, ao lado da key, e some quando a operação termina) nem onde o `SecureString` aparece em texto puro (no *state*). São os dois pontos da 0012 para retomar com recuperação espaçada.
- **Erro de partida no `rede.tf`:** ele copiou o exemplo da doc do `data "aws_vpc"`, que cria uma *subnet*: veio com `variable "vpc_id"`, `availability_zone` e `cidr_block` dentro do security group, e `us-west-2a`. Mostra que ainda não separa o *data source* do recurso que o exemplo cria. Depois do apontamento, ele começou o esqueleto (`default = true` certo) e pediu: "preencha ela logo".
- **A regra "ele escreve o Terraform" foi suspensa por ele nesta aula:** pediu que a IA preenchesse `rede.tf`, `iam.tf`, `user_data.sh`, `ec2.tf` e `outputs.tf`, rodasse o `plan`, o `nmap` e o `destroy`, e abrisse o PR. Ele rodou o `apply`, as sessões do SSM e o túnel. Ele não disse se a mudança vale de vez.
- **`validate` e `plan` não provam o `apply`.** O `plan` mostrou o texto `resolve:ssm:...` sem conferir, e o erro só apareceu quando o provider falou com a API. Isso vale para a revisão de qualquer PR de Terraform.
- PowerShell 5.1 quebra o `\"` dentro de argumentos para programas externos (`gh --jq`, `git commit -F -` com here-string). Contornos: `ConvertFrom-Json` e o bash do Git.

**Implicações:**
- Aula 0014: o aquecimento retoma o `.tflock` e o *state* com segredo. A regra de escrita precisa ser **perguntada no começo**, e não presumida.
- A RAM real no EC2 dá ~480 MiB de folga para o Prometheus e o Grafana. Swap 0: um pico vira OOM, não lentidão. Um swap pequeno no `user_data` fica como opção na etapa 13.
- Rotina de custo confirmada: `destroy` no fim da sessão. Por isso, **o que deve sobreviver ao `destroy`** (o Budget) não pode morar no mesmo *state* do EC2.
