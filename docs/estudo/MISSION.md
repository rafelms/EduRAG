# Missão: DevSecOps na prática com o EduRAG

## Por quê
Aprender DevSecOps fazendo: construir com as próprias mãos a pipeline do EduRAG até o deploy na AWS, seguindo o [pipeline-plano.md](../pipeline-plano.md), e guardar a prova de cada portão (PRs barrados, deploy, rollback) como evidência para o currículo.

## Sucesso é
- Escrever e explicar cada workflow da pipeline sem copiar de pronto.
- Ter a `main` protegida: nada entra sem PR e sem CI verde.
- Provar cada portão de segurança com um PR proposital que é barrado (segredo, SAST, dependência, imagem).
- Ver um merge na `main` chegar sozinho ao EC2 e um deploy quebrado voltar sozinho.
- Ter os prints e links desses PRs organizados para o currículo.

## Restrições
- Regra da Camada B: o Rafael escreve e configura; a IA explica e revisa.
- Orçamento da AWS baixo: alerta de gastos primeiro, nada de serviço caro (EKS fica de fora).
- Segue a ordem das etapas do plano; cada etapa só começa com a anterior verde.

## Fora do escopo (por enquanto)
- Kubernetes (F6), até a etapa 8 estar pronta.
- Observabilidade e LLMOps (F4 e F5).
