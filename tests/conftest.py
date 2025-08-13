import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="function")
def client():
    # fresh client per test to avoid leaking in-memory state across tests
    return TestClient(app)
