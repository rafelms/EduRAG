# Aula 0011 concluída: a conta é da experiência "AWS (new)", e isso mudou o roteiro

A aula 0011 foi feita por ele em 18/11/2026, passo a passo no chat. No primeiro print do Billing apareceram "Projetos" e "Equipe": a conta foi criada pelo **"Sign up for AWS (new)"**, o caso em que a aula mandava parar. As fontes foram conferidas na hora, e ele escolheu **manter a conta** em vez de ativar os recursos avançados (irreversível, exige o plano pago) ou criar outra conta.

**Evidence:**
- Plano gratuito, **US$ 100** de crédito, 180 dias (até 15/05/2027), valor devido US$ 0,00. Projeto "Next Big Thing".
- Região do projeto: **`us-east-2` (Ohio)**, fixada pelo país do endereço (Brasil). Não é a `us-east-1` da aula.
- MFA configurado no **AWS Builder ID**. Não há root nem tela de access keys no projeto.
- Budget **`edurag-mensal`**: modelo "Orçamento de custo mensal", US$ 15, alertas em 85% e 100% do gasto real e 100% do previsto. Filtro do modelo: **tipos de cobrança excluídos `Credit` e `Refund`**, ou seja, o Budget mede o custo **antes** dos créditos.
- AWS CLI **2.41.0**. `aws login --profile edurag` com região `us-east-2`. O `sts get-caller-identity` devolveu `assumed-role/AccountFullAccessRole/<id do Builder ID>`, na conta do projeto.
- Terraform **1.17.2**: SHA256 do zip igual à linha `windows_amd64` do `SHA256SUMS` (`2244b7a3…2a53024`). Ele colou só a linha publicada, e o professor calculou o hash do arquivo baixado para fechar a comparação.
- Plugin do Session Manager instalado ("installed successfully"). `git status` limpo.
- Quiz da aula respondido por ele.

**Insights:**
- Nessa experiência, a AWS gerencia uma Organization com SCPs que não podem ser mudadas. Três delas mudam a trilha:
  - `iam:*LoginProfile*` negado: usuário IAM não ganha senha de console. O papel do "usuário do dia a dia" fica com o Builder ID + `aws login`, que entrega credencial temporária de uma role (`AccountFullAccessRole`).
  - `iam:*Provider*` negado: **não dá para criar o provedor OIDC do GitHub**. Isso tira o OIDC da aula 0014 e o jeito previsto de autenticar o deploy da etapa 11.
  - `RegionFloor`: só a região do projeto (mais `us-east-1` e `us-west-2` para serviços globais).
- O **spend limit** dessa experiência (que pausa o projeto ao estourar) exige o plano pago. No plano gratuito, o teto é o próprio plano, que não cobra além dos créditos.
- A lacuna "o Budget conta antes ou depois dos créditos?" (RESOURCES) foi respondida: o modelo exclui `Credit` e `Refund`, então o alerta dispara pelo uso real mesmo com o crédito pagando.
- S3, SSM, IAM (roles), KMS, EC2 e STS estão liberados no plano gratuito da SCP. A aula 0012 não muda de forma.

**Implicações:**
- Toda a etapa 10 passa a usar **`us-east-2`**. Os preços da referência são de `us-east-1`; conferir os de Ohio na Calculator antes da aula 0013.
- Aula 0014: o portão de IaC (`fmt`, `validate`, `trivy config`) não precisa de credencial da AWS e continua igual. Sai o OIDC.
- **Decisão pendente dele, até a aula 0014:** como o deploy da etapa 11 entra no EC2 sem OIDC. Opções: (a) usuário IAM só com access key, guardada no GitHub, com permissão mínima de `ssm:SendCommand` (a SCP não nega `CreateUser` nem `CreateAccessKey`, mas é credencial de longa duração); (b) deploy por *pull*: a própria instância busca a tag nova no GHCR, sem credencial da AWS fora da conta; (c) ativar os recursos avançados (irreversível, plano pago, perde o spend limit).
- O ID da conta aparece no `Arn`. Não é segredo, mas, para não expor no repositório público, o nome do bucket do *state* usa um sufixo aleatório, e não o ID.
