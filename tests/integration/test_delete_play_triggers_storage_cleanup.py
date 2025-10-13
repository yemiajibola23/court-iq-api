import pytest
from app.main import app
from app.core.interfaces import StorageClient


class FakeStorage(StorageClient):
    def __init__(self, fail_for=None):
        self.calls = []
        self.fail_for = set(fail_for or [])
    
    def delete_blob(self, path: str):
        if path in self.fail_for:
            raise Exception("Simulated storage failure")
        else:
            print(f"[StubStorage] delete_blob called for: {path}")
        self.calls.append(path)

@pytest.fixture
def fake_storage():
    return FakeStorage()

def test_delete_endpoint_triggers_storage_cleanup(client, fake_storage):
    # Arrange
    app = client.app
    try:
        from app.deps import get_storage_client
        app.dependency_overrides[get_storage_client] = lambda: fake_storage
    except ImportError:
        pytest.skip("Could not import get_storage_client from app.deps")
        
    try:
        payload = {"title": "Test Play", "video_path": "https://example.com/xyz.mp4"}
    
        create_res = client.post("/v1/plays", json=payload)
        assert create_res.status_code == 201, create_res.text
        play_id = create_res.json()["id"]
    
        # Act 
        delete_res = client.delete(f"/v1/plays/{play_id}")
    
        # Assert
        assert delete_res.status_code == 204
        assert fake_storage.calls == [payload["video_path"]]
    finally:
        app.dependency_overrides.pop(get_storage_client, None)  # Clean up overrides