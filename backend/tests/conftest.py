import os
import tempfile
import pytest

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(
    tempfile.gettempdir(), "ner_link_test.db"
)

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base, SessionLocal


@pytest.fixture(scope="function", autouse=True)
def reset_db():
    """Every test starts with a clean, empty schema."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
