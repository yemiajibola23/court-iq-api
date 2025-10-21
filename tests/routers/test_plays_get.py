# TECH_DEBT: TD7 — add malformed UUID tests for GET /v1/plays/{id}.
# TECH_DEBT: TD8 — add fixture to reset in-memory store between tests.

def test_get_play_returns_404_when_id_doesnt_exist(client):
    fake_id="00000000-0000-0000-0000-000000000000"
    
    res = client.get(f"/v1/plays/{fake_id}")
    
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Play not found"

def test_get_play_returns_200_and_play_dto_after_create(client):
    payload = {"title": "Spain PnR", "video_path": "https://example.com/clip.mp4"}
    
    create_res = client.post("/v1/plays", json=payload)
    assert create_res.status_code == 201
    assert "Location" in create_res.headers
    
    location = create_res.headers["Location"]
    assert location.startswith("/v1/plays/")
    play_id = location.rsplit("/", 1)[-1]
    
    res = client.get(f"/v1/plays/{play_id}")
    
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")

    body = res.json()
    assert set(body.keys()) >= {"id", "title", "video_path"}
    assert body["id"] == play_id
    assert body["title"] == "Spain PnR"
    assert body["video_path"] == "https://example.com/clip.mp4"
    
    
def test_get_play_includes_video_and_thumbnail_url(client):
    # Arrange
    payload = {"title": "Spain PnR", "video_path": "https://example.com/clip.mp4"}
    
    create_res = client.post("/v1/plays", json=payload)
    assert create_res.status_code == 201
    play_id = create_res.headers["Location"].rsplit("/", 1)[-1]
    
    # Act
    res = client.get(f"/v1/plays/{play_id}")
    assert res.status_code == 200
    body = res.json()
    
    assert set(body.keys()) >= {"id", "title", "video_path"}
    
    
    assert "videoUrl" in body and body["videoUrl"] is None
    assert "thumbnailUrl" in body and body["thumbnailUrl"] is not None
    
    
def test_get_play_uses_thumbnail_placeholder_when_enabled(client, set_env_and_reload):
    # Arrange
    set_env_and_reload(thumbnail_placeholder_mode="static",thumbnail_placeholder="/static/placeholders/thumb-480x270.png")
    
    payload = {"title": "Spain PnR", "video_path": "https://example.com/clip.mp4"}
    
    create_res = client.post("/v1/plays", json=payload)
    play_id = create_res.headers["Location"].rsplit("/", 1)[-1]
    
    # Act
    res = client.get(f"/v1/plays/{play_id}")
    body = res.json()
    
    # Assert
    assert "thumbnailUrl" in body
    assert body["thumbnailUrl"] == "/static/placeholders/thumb-480x270.png"
    

def test_get_play_malformed_uuid_returns_422(client):
    bad_id = "not-a-uuid"
    r = client.get(f"/v1/plays/{bad_id}")
    assert r.status_code == 422
    body = r.json()
    
    assert "detail" in body
    assert "invalid UUID" in body["detail"]