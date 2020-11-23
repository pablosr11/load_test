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
######


@pytest.fixture(scope="session", autouse=True)
def delete_database_file_on_completion(request):
    """Cleanup testing db once we are finished."""

    def remove_test_dir():
        os.remove(TEST_DB_PATH)

    request.addfinalizer(remove_test_dir)


@pytest.fixture(scope="function", autouse=True)
def drop_all_tables(request):
    """Cleanup testing db once we are finished."""

    def remove_tables():
        Base.metadata.drop_all(bind=engine)

    request.addfinalizer(remove_tables)


@pytest.fixture()
def test_app(monkeypatch):

    # DB patch
    monkeypatch.setattr("sqlalchemy.create_engine", Mock(return_value=engine))

    # Redis patch
    monkeypatch.setattr(
        "server.caches.redis_client.get_redis_client", fakeredis.FakeStrictRedis
    )

    # Create tables | should we do this on event instead of when you need the app?
    Base.metadata.create_all(bind=engine)

    # Imports cant go on top level as we have to patch the connections first. TODO.
    from server.main import app

    return app


@pytest.fixture(autouse=True)
def client(test_app):
    return TestClient(test_app)
