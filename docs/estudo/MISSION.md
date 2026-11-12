# Missão: DevSecOps, IaC e observabilidade na prática com o EduRAG

## Por quê
Aprender fazendo: construir com as próprias mãos a pipeline do EduRAG, subir a infraestrutura na AWS com **Terraform** e observar a aplicação no ar com **Prometheus + Grafana**, seguindo o [pipeline-plano.md](../pipeline-plano.md). Guardar a prova de cada portão, do deploy e dos alertas como evidência para o currículo.

## Contexto (redefinido em 12/11/2026)
- O EduRAG **não** fica aberto ao público. O ambiente de produção é privado, só para o Rafael, e existe **só até o fim desta trilha**. Depois, `terraform destroy`.
- Por isso, a segurança é dimensionada para "privado e temporário": rede fechada, segredos fora do repositório e teto de gastos. A blindagem para acesso público (login, cota, CORS) fica fora do escopo.

## Sucesso é
- Escrever e explicar cada workflow e cada arquivo Terraform sem copiar de pronto.
- Ter a `main` protegida: nada entra sem PR e sem CI verde (feito).
- Provar cada portão de segurança com um PR barrado (feito: segredo, SAST, dependência, imagem) e acrescentar o portão de IaC.
- Subir a infraestrutura inteira com `terraform apply` e derrubá-la com `terraform destroy`, sem clique no console além do *bootstrap*.
- Ver um merge na `main` chegar sozinho ao EC2 e um deploy quebrado voltar sozinho.
- Ver no Grafana a latência do LLM e o gasto em tokens, e um alerta disparar quando a API cai.
- Ter os prints e links organizados para o currículo antes do `destroy`.

## Restrições
- Regra da Camada B: o Rafael escreve e configura; a IA explica e revisa.
- Orçamento baixo: alerta de gastos na AWS e teto de gastos na Anthropic antes de qualquer recurso pago. Nada de serviço caro (EKS, NAT Gateway, RDS ficam de fora).
- Nenhuma porta de entrada aberta para a internet: acesso pelo túnel do SSM (decisão a confirmar na etapa 10).
- Segue a ordem das etapas do plano; cada etapa só começa com a anterior verde.

## Fora do escopo
- Exposição pública: autenticação de usuários, cota por usuário, CORS e cabeçalhos (as antigas aulas 0011 a 0013). Voltam só se o projeto um dia for público.
- Domínio e HTTPS públicos.
- LLMOps (F5) e Kubernetes (F6).
