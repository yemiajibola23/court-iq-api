from app.utils.cursor import decode_cursor
from datetime import timezone
from uuid import UUID

def test_list_returns_next_cursor_and_has_more(client, seed_many_plays):
    # Arrange
    seed_many_plays([{"title": f"Alpha Cut {i}"} for i in range(3)])
    
    # Act
    res = client.get("/v1/plays", params={"limit": 2})
    
    # Assert
    assert res.status_code == 200
    payload = res.json()
    assert set(payload.keys()) >= {"data", "nextCursor", "hasMore"}
    
    items = payload["data"]
    assert isinstance(items, list)
    assert len(items) == 2
    
    assert payload["hasMore"] is True
    assert isinstance(payload["nextCursor"], str) and payload["nextCursor"]
    
    
def test_list_uses_cursor_for_second_page(client, seed_many_plays):
    # Arrange
    seed_many_plays([{"title": f"Alpha Cut {i}"} for i in range(3)])
    
    # Page 1
    r1 = client.get("/v1/plays", params={"limit": 2})
    assert r1.status_code == 200
    p1 = r1.json()
    next_cursor = p1["nextCursor"]
    assert isinstance(next_cursor, str) and next_cursor
    
    # Page 2
    r2 = client.get(f"/v1/plays", params={"limit": 2, "cursor": next_cursor})
    assert r2.status_code == 200
    p2 = r2.json()
    
    items2 = p2["data"]
    assert isinstance(items2, list)
    assert len(items2) == 1
    assert p2["hasMore"] is False
    assert p2["nextCursor"] is None
    
def test_list_rejects_bad_cursor(client, assert_422_field):
    # Act
    res = client.get("/v1/plays", params={"cursor": "not-a-real-token"})
    
    # Assert
    assert_422_field(res, "cursor", contains="invalid cursor token")
    
def test_list_next_cursor_is_opaque_and_decodes(client, seed_many_plays):
    # Arrange
    seed_many_plays([{"title": f"Alpha Cut {i}"} for i in range(3)])
    
    r1 = client.get("/v1/plays", params={"limit": 2})
    payload = r1.json()
    items = payload["data"]
    cursor = payload["nextCursor"]
    
    # opaque-ish shape
    assert isinstance(cursor, str) and cursor
    assert "=" not in cursor and "{" not in cursor
    
    # decode & check
    dt, uid = decode_cursor(cursor)
    assert dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) == timezone.utc.utcoffset(dt)
    assert isinstance(uid, UUID)
    
    # compare items on last page
    last = items[-1]
    r2 = client.get("/v1/plays", params={"limit": 2, "cursor": cursor})
    p2 = r2.json()
    assert len(p2["data"]) == 1