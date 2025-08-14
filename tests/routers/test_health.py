from fastapi.testclient import TestClient
from app.main import app

def test_create_minimal_play():
    c = TestClient(app)
    payload = {"title": "Test Play", "video_path": "gs://bucket/plays/demo/raw.mp4"}
    r = c.post("/v1/plays", json=payload)
    
    assert r.status_code == 200
    
    body = r.json()
    assert "playId" in body and isinstance(body["playId"], str)