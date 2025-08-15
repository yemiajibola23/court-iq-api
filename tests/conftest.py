import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.plays_repo import clear_store
from typing import Callable, List, Dict, Optional

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

@pytest.fixture(autouse=True)
def _reset_repo_state():
    clear_store()

@pytest.fixture(scope="function")
def seed_many_plays(client) -> Callable[[List[Dict]], List[Dict]]:
    """
    Returns a function that accepts a list of play stubs and seeds them via POST /v1/plays.
    Each stub should at least include {'title': '...'}.
    Returns the list of created Play DTOs (in the same order).
    """
    def _seed(stubs: List[Dict]) -> List[Dict]:
        created: List[Dict] = []
        for i, stub in enumerate(stubs, start=1):
            # Minimal valid payload 
            payload = {
                "title": stub["title"],
                "video_path": stub.get("video_path", f"https://example.com/clip{i}.mp4")
            }
            
            # POST to create
            res = client.post("/v1/plays", json=payload)
            assert res.status_code == 201, res.text
             
            location = res.headers.get("Location")
            assert location and location.startswith("/v1/plays/"), f"Missing Location header: {res.headers}"

            # fetch the created resource to get a DTO with 'id'
            show = client.get(location)
            assert show.status_code == 200, show.text
            created.append(show.json())
            
        return created
    
    return _seed