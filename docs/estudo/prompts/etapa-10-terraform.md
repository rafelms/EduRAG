# Prompt para o /teach: etapa 10 (base na AWS com Terraform)

> Como usar: rode `/teach` e cole o bloco abaixo. Ele é o contexto da aula, não a aula pronta.

---

Monte o plano de estudos e a primeira aula da **etapa 10 do EduRAG: a base na AWS com Terraform**. Eu vou escrever todo o Terraform e configurar a AWS com as minhas mãos. Você explica o porquê, dá o roteiro e revisa.

## Leia antes, nesta ordem

1. `docs/estudo/MISSION.md`: objetivo, restrições e o que está fora do escopo.
2. `docs/pipeline-plano.md`, **etapa 10** (e a 11, para saber o que a 10 precisa deixar pronto).
3. `docs/estudo/NOTES.md`: como eu aprendo e o que já funcionou ou não.
4. `docs/estudo/learning-records/0010` a `0012`: GHCR público, auditoria de segredos, teto de gastos e Sonnet 5.
5. Uma aula existente como modelo de formato: `docs/estudo/lessons/0008-publicar-no-ghcr.html`. Use os mesmos `assets/` (`style.css`, `checklist.js`, `quiz.js`) e o glossário `reference/glossario.html`.
6. `docker-compose.yml` e `Dockerfile`: o que vai rodar no EC2.

## Quem sou eu

- Já sei GitHub Actions e a pipeline de segurança deste repositório (etapas 0 a 9 feitas e provadas).
- **AWS e Terraform são novos para mim.** São o que eu quero aprender, junto com Prometheus e Grafana nas etapas 12 a 14.
- Máquina: **Windows, PowerShell e Docker Desktop.** Comandos em PowerShell, sem `\` de continuação de linha.
- Gosto de texto direto, com tabelas e sem enrolação. Aprendo melhor com o porquê antes do como, uma prova concreta no fim e recuperação espaçada (perguntas que retomam aulas anteriores).
- Na etapa 7, um **esqueleto sem valores** funcionou melhor que "só apontar as linhas". Na etapa 8, eu escrevi sem esqueleto. Comece sem e ofereça o esqueleto se eu travar.

## Regras

- **Eu escrevo o HCL e configuro a AWS.** Não entregue arquivos `.tf` prontos nem blocos completos para copiar. Pode mostrar a forma de um recurso (nome do tipo, argumentos que importam, link da documentação do provider) e o que conferir no `plan`.
- **Confira as fontes na hora**, não de memória: versão atual do Terraform e do provider `hashicorp/aws`, preços em `us-east-1` (EC2, EBS gp3, IPv4 público, S3), as regras atuais do *free tier* e a documentação do backend S3 (trava com `use_lockfile`). Cite a fonte em cada afirmação técnica, como nas aulas anteriores.
- **Custo primeiro:** o alerta do Budgets vem antes de qualquer recurso pago. Diga quanto cada recurso custa por hora e por mês, e ensine a desligar (`stop`) ou destruir quando eu não estiver estudando.
- **Segredos:** nenhuma access key no repositório nem no `.tf`. Valor de segredo não entra em recurso do Terraform, porque vai para o *state*. Os valores do Parameter Store são gravados à mão com `aws ssm put-parameter`. O gitleaks continua de pé.
- **Nenhuma porta de entrada aberta:** o security group nasce sem regras de entrada, e o acesso é pelo túnel do SSM.

## Decisões já tomadas (não reabra)

| Tema | Decisão |
| --- | --- |
| Região | `us-east-1` |
| Acesso ao EC2 | Túnel do SSM (`AWS-StartPortForwardingSession`), sem SSH e sem porta aberta |
| Registro de imagens | GHCR (pacotes públicos), sem ECR |
| Embeddings | Ollama no EC2 (`nomic-embed-text`). O LLM é o Claude Sonnet 5, pela API |
| Ambiente | Privado e temporário: `terraform destroy` na etapa 15 |
| Fora do escopo | EKS, NAT Gateway, RDS, domínio e HTTPS públicos |

## O que a etapa 10 precisa entregar

Do `pipeline-plano.md`:
- **Bootstrap à mão:** MFA no root, alerta no AWS Budgets, usuário do dia a dia com MFA (IAM Identity Center, `aws sso login`), bucket S3 do *state* (versionado, criptografado, sem acesso público).
- **Terraform em `infra/`:** EC2 Amazon Linux 2023 com *instance profile* do SSM; `user_data` com Docker e o plugin do compose; security group sem entrada; provedor OIDC do GitHub e uma role mínima (`ssm:SendCommand` só nessa instância); permissão para a instância ler os parâmetros do Parameter Store; `import` do Budget.
- **Portão de IaC na CI:** `terraform fmt -check`, `terraform validate` (com `init -backend=false`) e `trivy config infra/` como check obrigatório.
- **Provas:** um PR abrindo a porta 22 para `0.0.0.0/0` é barrado pelo portão; `terraform apply` sobe tudo do zero; a interface abre pelo túnel do SSM; um `nmap` de fora não acha porta aberta; medir a RAM do EC2 com a stack de pé.

## Como dividir (sugestão; ajuste se achar melhor)

| Aula | Conteúdo | Prova |
| --- | --- | --- |
| 0011 | Conceitos (*state*, `plan` × `apply`, provider, por que IaC num ambiente temporário). Bootstrap da conta, CLI, Terraform e Session Manager plugin. Bucket do *state* e o primeiro ciclo `init` → `plan` → `apply` → `destroy` com um recurso grátis | O `destroy` deixa a conta como estava |
| 0012 | EC2, security group sem entrada, role e *instance profile* do SSM, `user_data`. Túnel do SSM até a interface. Medir a RAM | Interface aberta pelo túnel; `nmap` de fora sem porta |
| 0013 | OIDC do GitHub e role mínima, Parameter Store, `import` do Budget, portão de IaC na CI | PR com a porta 22 aberta barrado |

## O que gerar

- `docs/estudo/lessons/0011-*.html`, no formato das aulas anteriores: aquecimento de memória, o porquê, conceitos com fonte, mão na massa em checklist, "me conte" no fim e um quiz de recuperação que retome as aulas 0008 e 0009 e os registros 0011 e 0012.
- Uma referência nova em `docs/estudo/reference/` (Terraform e AWS: comandos, recursos, custos e armadilhas) e os termos novos no `glossario.html`.
- As fontes em `docs/estudo/RESOURCES.md`, com "Usar para:".
- O mapa das aulas 0011 a 0013 na etapa 10 do `pipeline-plano.md`.

O "pronto quando" da etapa 10: `terraform apply` sobe a máquina do zero, eu abro a interface pelo túnel do SSM e um `nmap` de fora não acha nenhuma porta aberta.
