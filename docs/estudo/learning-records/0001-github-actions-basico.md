# Já escreve workflows básicos do GitHub Actions

Ele escreveu sozinho o `ci.yml` das etapas 1 e 2: jobs paralelos, `services` com Postgres e health check, cache do `uv` e do npm, `npm ci`, artefato de cobertura. Também entende tag × SHA nas actions. As anotações estão em [estudo-ci.md](../../estudo-ci.md).

**Implicações:** não reensinar a sintaxe de workflow. As próximas aulas podem partir de `on`, `jobs`, `steps`, `uses` e `run` como conhecidos. O conceito novo da etapa 3 é a CI deixar de ser só um aviso e virar um portão.
