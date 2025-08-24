import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.memory import MemoryRepository
from typing import Callable, List, Dict, Optional
import uuid
from app.deps import get_repo

@pytest.fixture(scope="function")
def client():
    # fresh client per test to avoid leaking in-memory state across tests
    app.dependency_overrides[get_repo] = lambda: MemoryRepository()
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def assert_201_field():
    def _assert(res):
        assert res.status_code == 201
        data = res.json()
        assert "playId" in data
        
        # Validate UUID-ish value (FastAPI serializes UUID -> string)
        uuid_val = data["playId"]
        uuid.UUID(uuid_val)
    
        assert "Location" in res.headers
        # Location header
        location = res.headers["Location"]
        assert location.startswith("/v1/plays/")

        # The id in Location should equal the JSON playId
        loc_id = location.rsplit("/", 1)[-1]
        assert loc_id == uuid_val
        
    return _assert

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