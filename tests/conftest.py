import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="function")
def client():
    # fresh client per test to avoid leaking in-memory state across tests
    return TestClient(app)


@pytest.fixture
def assert_422_field():
    def _assert(res, field: str):
        assert res.status_code == 422
    
        data = res.json()
        assert "detail" in data and isinstance(data["detail"], list)
    
        # be flexible about FastAPI/Pydantic error shape but ensure it references 'title'
        assert any(
            (field in err.get("loc", [])) or
            (isinstance(err.get("loc"), list) and field in err["loc"])
            for err in data["detail"]
        )
    return _assert