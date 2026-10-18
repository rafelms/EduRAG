# Ruleset da main criado e provado

Ele configurou o ruleset `protege-main` sozinho e fez as duas provas: o push direto foi recusado com `GH013: Repository rule violations` (exigindo PR e os 2 checks), e o PR #1, com teste quebrado, ficou com o merge bloqueado (`backend` falhou, `frontend` passou, os dois marcados como *Required*).

**Evidence:** prints do terminal e do PR #1, em 18/10/2026.

**Tropeço:** ele não desfez o commit local da prova 1 antes de criar a branch da prova 2, então o commit `teste: push direto` foi junto para o PR. Isso mostra que ele ainda não tinha o modelo mental de "a branch nasce de onde eu estou e leva todos os commits que vieram antes". Vale reforçar na próxima aula, e o fluxo por PR (branch → PR → merge → pull) ainda precisa ser praticado.
