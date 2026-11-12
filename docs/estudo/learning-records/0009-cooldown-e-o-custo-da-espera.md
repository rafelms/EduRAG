# Etapa 6 fechada: cooldown de 7 dias e o custo real da espera

O uv só aceita versões publicadas há 7 dias ou mais (`exclude-newer = "7 days"` no `pyproject.toml`), e o Dependabot espera o mesmo prazo no bloco `uv` (`cooldown: default-days: 7`), para não propor mínimos que o uv ainda recusa. Entrou no [PR #38](https://github.com/rafelms/EduRAG/pull/38), mesclado em 04/11/2026, e zerou o aviso `uv-missing-dependency-cooldown` do Semgrep. Com isso, a etapa 6 está inteira.

**Evidence:**
- Commit `e742423` (03/11): o `uv.lock` ganhou só o bloco `[options]` (`exclude-newer-span = "P7D"`), sem trocar nenhuma versão, como a aula 0007 previa.
- No #38, o `trivy-fs` ficou vermelho com 7 HIGH novos na `pypdf 6.21.2` (DoS por PDF), corrigidos na 6.21.4, publicada em 28/10 às 17:00 UTC. Ele escolheu **esperar sem isenção** até 04/11.
- No caminho, o [PR #42](https://github.com/rafelms/EduRAG/pull/42) do Dependabot (`python-menores`), mesclado antes do #38, trouxe `pypdf>=6.21.4` e `python-multipart>=0.0.33`. Quando ele foi aberto, a `main` ainda não tinha cooldown no Dependabot. As duas versões tinham menos de 7 dias.
- Commit `0a81e58` (04/11, no #38): isenção temporária `exclude-newer-package = { pypdf = false, python-multipart = false }`, com prazo no comentário (07/11, 11:23 BRT). Sem ela, o `uv lock --check` passava, mas qualquer nova resolução (`--upgrade` ou dependência nova) falhava.
- 12/11: isenção removida no [PR #47](https://github.com/rafelms/EduRAG/pull/47), com todos os checks verdes. Testado antes num container (`python:3.12-slim` + `uv==0.13.1`): o `uv lock` só apaga o bloco `[options.exclude-newer-package]` e não rebaixa nada.

**Insights:**
- O cooldown e a correção de segurança puxam para lados opostos: o portão do Trivy exige a versão nova, e o cooldown a recusa por 7 dias. A válvula de escape é a isenção **por pacote**, nunca desligar o cooldown inteiro.
- Uma isenção sem data de validade vira permanente. O comentário com o prazo funcionou: a remoção foi feita, com 5 dias de atraso.
- O uv e o Dependabot precisam do mesmo prazo, e configurados **juntos**. O #42 entrou num momento em que só um dos lados estava pronto, e o lock passou a depender de versões que o uv recusaria.
- Esperar 7 dias por uma correção de DoS foi aceitável aqui, porque a API não está exposta. Num sistema público, a decisão seria isentar logo e registrar o motivo.

**Implicações:**
- Regra prática: correção de segurança com menos de 7 dias → isenção por pacote, com data de remoção no comentário e um PR só para tirá-la.
- A observar: como fica um *security update* do Dependabot que propõe uma versão com menos de 7 dias. O `cooldown` do Dependabot não segura esse tipo de PR, mas o `exclude-newer` do uv continua valendo, e o lock pode falhar no próprio PR.
