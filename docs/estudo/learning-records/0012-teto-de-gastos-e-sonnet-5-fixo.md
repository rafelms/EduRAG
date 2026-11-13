# Aula 0009 concluída e Claude ligado: US$ 5 por mês, só o Sonnet 5

O Console da Anthropic foi configurado por ele em 13/11/2026, e o adaptador `ClaudeLLM` entrou no PR `feat/claude-llm`. Desta vez, **a pedido dele, o código foi escrito pela IA**; ele monta o `.env` e faz o primeiro teste real.

**Evidence:**
- Teto de gastos: **US$ 5/mês na organização e US$ 5/mês no workspace `edurag`**. Alertas sugeridos em US$ 2,50 e US$ 4,00.
- Limites de taxa do Sonnet 5 no workspace: **15 mil** tokens de entrada/min, **4 mil** de saída/min, **5** requisições/min. A primeira tentativa (2 mil de entrada) barraria toda pergunta: uma pergunta com `top_k=5` tem ~6.600 tokens, e o limite de entrada é estimado no início da requisição.
- Chave `edurag-dev` criada no workspace e guardada só no `.env` local.
- Decisões: embeddings no **Ollama** (sem migration, sem segunda chave); acesso ao prod pelo **túnel do SSM**; modelo **`claude-sonnet-5`, e só ele**.
- Suíte: 81 testes passando com Postgres (eram 59), `ruff` limpo, lint e build do front limpos.

**Insights:**
- O modelo é um campo da requisição que o nosso código monta. Um prompt injection num PDF muda o **texto** da resposta, nunca o `model` da próxima chamada. Ele só mudaria se a API aceitasse o modelo do cliente (o `AskRequest` não tem esse campo) ou se o LLM tivesse ferramentas (o EduRAG faz uma chamada só, sem ferramentas). Há um teste para isso: `test_prompt_injection_na_resposta_nao_muda_a_proxima_chamada`.
- A allowlist (`ALLOWED_CLAUDE_MODELS` em `app/config.py`) faz a API **não subir** com outro modelo, mesmo com um `.env` ou uma variável do EC2 errada. O adaptador confere de novo.
- Sem `fallbacks`: o fallback de recusa da Anthropic re-executa a pergunta **em outro modelo**, o que quebraria a regra. Uma recusa vira "Não encontrei".
- O Console não tem (na documentação de 13/11) um jeito de restringir uma chave a um modelo. A garantia fica no código; no Console, os outros modelos ficam com o menor limite aceito.
- Limite de taxa não segura o gasto do mês, quem segura é o teto. O limite define a velocidade do pior caso: com 15 mil/4 mil, um bug levaria mais de uma hora para queimar os US$ 5, tempo de ver o alerta.
- O limite de entrada acabou servindo de teto para o `top_k`. Ele foi baixado de 20 para 10 na API e no front.

**Implicações:**
- Etapa 12: os tokens de entrada e saída já saem no log de cada chamada (`chamada ao claude`). Viram contador no `/metrics`.
- Etapa 10: a chave de produção (`edurag-prod`) nasce no mesmo workspace e vai só para o Parameter Store.
- O `/ready` agora separa `embeddings` de `llm`. O smoke test da etapa 11 sabe qual dos dois caiu.
