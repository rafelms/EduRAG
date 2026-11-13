"""Configuração comum dos testes.

A DATABASE_URL é obrigatória na aplicação, e o `app.main` monta a config já no
import. Os testes em memória nunca conectam nessa URL; os de PostgreSQL trocam
por TEST_DATABASE_URL (ver tests/integration/conftest.py).
"""

import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://teste:teste@localhost:5432/nao-usado")
