
def test_list_plays_pagination_happy_path(client, seed_many_plays):
    # Arrange
    created = seed_many_plays([
        {"title": "Alpha Cut"},
        {"title": "Alpha Spain"},
        {"title": "Bravo Ghost"},
        {"title": "Charlie Spain"},
        {"title": "Delta Split"},
    ])
    
    # Page 1
    r1 = client.get("/v1/plays", params={"limit": 2})
    b1 = r1.json()
    
    assert r1.status_code == 200
    assert [p["title"] for p in b1["data"]] == ["Alpha Cut", "Alpha Spain"]
    assert b1["nextCursor"] == created[1]["id"]
    
    # Page 2
    r2 = client.get("/v1/plays", params={"limit": 2, "cursor": b1["nextCursor"]})
    b2 = r2.json()
    
    assert r2.status_code == 200
    assert [p["title"] for p in b2["data"]] == ["Bravo Ghost", "Charlie Spain"]
    assert b2["nextCursor"] == created[3]["id"]
    
    
    # Page 3
    r3 = client.get("/v1/plays", params={"limit": 2, "cursor": b2["nextCursor"]})
    b3 = r3.json()
    
    assert r3.status_code == 200
    assert [p["title"] for p in b3["data"]] == ["Delta Split"]
    assert b3.get("nextCursor") in (None, )