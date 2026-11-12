# Auditoria de segredos antes da nuvem: histórico limpo

Antes de criar as primeiras chaves reais (Anthropic e AWS), o histórico inteiro do repositório público foi varrido atrás de segredos, inclusive o que só existe no GitHub. Feito em 12/11/2026, a pedido dele, junto com a redefinição do escopo da reta final (prod privado e temporário).

**Evidence:**
- `gitleaks` v8.21.2 via Docker, `git --log-opts="--all"`: 65 commits do histórico local, **nenhum achado**.
- Os PRs fechados sem merge (#1, #3, #6, #9, #10, #14, #35, #36) continuam públicos em `refs/pull/N/head`, mesmo sem branch. Buscados com `git fetch origin pull/N/head` e varridos de novo: 73 commits, **1 achado**, a chave AWS falsa do PR #6 (`config-falsa.env`, commit `d15ba48`), que é a própria prova da etapa 4. As refs locais da auditoria foram apagadas depois.
- *Secret scanning* do GitHub (`gh api …/secret-scanning/alerts`): 0 alertas.
- `git log --all -- .env frontend/.env`: vazio. O `.env` local tem só configuração e a senha local do Postgres.
- Busca manual nas linhas adicionadas de todo o histórico por `password`, `secret`, `api_key`, `token`, `DATABASE_URL`: só `edurag:edurag` no Postgres de serviço da CI e o padrão `change-me` em `app/config.py`.

**Insights:**
- O gitleaks procura **formatos** conhecidos (chave AWS, `sk-ant-…`, tokens do GitHub). Uma senha comum como `edurag` não tem formato nem entropia: só a busca manual acha. Por isso as duas buscas se complementam.
- Fechar um PR não apaga os commits dele. Num repositório público, um segredo num PR fechado está tão vazado quanto um na `main`, e só sai com suporte do GitHub. Para um segredo real, a correção é sempre **revogar**, não reescrever o histórico.
- A chave do PR #6 só é inofensiva se foi inventada. Se tivesse vindo de uma conta real, o certo seria desativá-la no IAM.
- O `edurag:edurag` da CI é aceitável: o banco nasce e morre com o job e não guarda nada.
- O `change-me` é um risco diferente: um valor padrão de credencial faz a API subir "funcionando" sem configuração, com uma senha que está no repositório público. Melhor falhar ao subir.

**Implicações:**
- Tirar o padrão de `database_url` (`fix/config-sem-default`, etapa 9).
- Chaves novas nascem separadas por ambiente: `edurag-dev` (sua máquina) e `edurag-prod` (só no SSM Parameter Store). No fim da trilha, revogar a de produção (etapa 15).
- Valor de segredo não entra em recurso do Terraform: ele iria parar no *state*. O Terraform cria a permissão de leitura; o valor é gravado à mão.
