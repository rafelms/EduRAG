# O Trivy barrou um PR só de docs: portão de SCA funcionando fora de teste

O PR #15 (`atualizando-docs`, só arquivos em `docs/`) foi barrado pelo `trivy-fs`: 3 HIGH no `pypdf 6.20.1` (CVE-2026-115572, CVE-2026-115580 e CVE-2026-115585, DoS com PDF malformado), divulgadas depois do PR #13. Eu diagnostiquei (Trivy 0.76.1 local, mesma versão da CI) e fiz a correção na branch `fix/pypdf` (`uv lock --upgrade-package pypdf` → 6.21.2, testes e Trivy limpos). Ele abriu e fez o merge do PR #16, rebaseou a `atualizando-docs` na `main` nova, deu o force push e fez o merge do PR #15.

**Evidence:** PR #15 vermelho no `trivy-fs` em 27/10/2026; PR #16 (`1b15a41`) com merge na `main` (`5468e72`); PR #15 com merge depois do rebase (`9aa9818`).

**Tropeços:**
- A correção e o diagnóstico foram meus, não dele. Ele só viu o resultado. Vale a recuperação: "por que um PR sem código foi barrado?".

**Insights:**
- O `trivy-fs` olha o repositório inteiro, não o diff do PR. Uma CVE nova deixa vermelho qualquer PR, até um de docs. Na prática, isso força corrigir antes de seguir. É a lição do registro 0005 ("SCA fica vermelho sem commit novo") acontecendo de verdade.
- Ele resolveu sozinho o fluxo de rebase da branch de docs em cima da `main` corrigida.

**Implicações:**
- **Conflito entre cooldown e correção de segurança, agora concreto:** `pypdf 6.21.2` saiu em 21/10 e `certifi 2026.10.23` em 23/10. Com `exclude-newer = "7 days"`, o `uv lock` rebaixaria o `pypdf` para a 6.20.1 (vulnerável) até 28/10 e o `certifi` até 30/10. O cooldown derrubaria o `trivy-fs`. Esse é o exemplo da aula 0005 com dados reais, e ele decide: esperar, usar `exclude-newer-package` ou prazo menor.
- Ordem da parte 2: primeiro `ci/pin-actions` (independente), depois cooldown, depois `dependabot.yml`.
