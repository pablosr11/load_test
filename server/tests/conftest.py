import os
from unittest.mock import Mock

import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from server.database.models import Base

##### DB SETUP - Create engine to patch original and create Tables
TEST_DB_PATH = "./test.db"
engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False}
)
Base.metadata.create_all(bind=engine)
######


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Cleanup testing db once we are finished."""

    def remove_test_dir():
        os.remove(TEST_DB_PATH)

    request.addfinalizer(remove_test_dir)


@pytest.fixture()
def test_app(monkeypatch):

    # DB patch
    monkeypatch.setattr("sqlalchemy.create_engine", Mock(return_value=engine))

    # Redis patch
    monkeypatch.setattr(
        "server.caches.redis_client.get_redis_client", fakeredis.FakeStrictRedis
    )
    # Imports cant go on top level as we have to patch the connections first. TODO.
    from server.main import app

    return app


@pytest.fixture(autouse=True)
def client(test_app):
    return TestClient(test_app)
