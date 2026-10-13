"""Fixtures da API. O repositório roda em memória e, se TEST_DATABASE_URL estiver
definido, também contra um PostgreSQL real com pgvector (ver README)."""

import os

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.adapters.pg_repository import PgDocumentRepository
from app.config import Settings
from app.container import assemble_services
from app.db.session import create_db_engine, create_session_factory
from app.main import create_app
from tests.fakes import FakeEmbeddings, FakeLLM, InMemoryRepository

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")


@pytest.fixture(scope="session")
def pg_session_factory():
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL não definido")
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    from app.config import get_settings

    get_settings.cache_clear()
    command.upgrade(Config("alembic.ini"), "head")
    return create_session_factory(create_db_engine(TEST_DATABASE_URL))


@pytest.fixture(params=["memory", "postgres"])
def repository(request):
    if request.param == "memory":
        return InMemoryRepository()
    factory = request.getfixturevalue("pg_session_factory")
    with factory() as session:
        session.execute(text("TRUNCATE documents, chunks, questions CASCADE"))
        session.commit()
    return PgDocumentRepository(factory)


@pytest.fixture
def fakes(repository):
    return {"repository": repository, "embeddings": FakeEmbeddings(), "llm": FakeLLM()}


@pytest.fixture
def client(fakes):
    settings = Settings(max_upload_mb=1, min_score=0.3)
    services = assemble_services(settings, **fakes)
    with TestClient(create_app(services)) as test_client:
        yield test_client
