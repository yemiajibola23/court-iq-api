
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
    
def test_list_plays_title_prefix_filter_happy_path(client, seed_many_plays):
    _ = seed_many_plays([
        {"title": "Alpha Cut"},
        {"title": "Alpha Spain"},
        {"title": "Bravo Ghost"},
        {"title": "Charlie Spain"},
        {"title": "Delta Split"},
    ])

    # case-insensitive + trimmed prefix
    r = client.get("/v1/plays", params={"limit": 10, "title": "  alpha  "})
    b = r.json()

    assert r.status_code == 200
    assert [p["title"] for p in b["data"]] == ["Alpha Cut", "Alpha Spain"]
    # exactly two results → no more pages
    assert b.get("nextCursor") in (None,)

def test_list_plays_title_prefix_filter_with_pagination(client, seed_many_plays):
    created = seed_many_plays([
        {"title": "Alpha Cut"},
        {"title": "Alpha Spain"},
        {"title": "Bravo Ghost"},
        {"title": "Charlie Spain"},
        {"title": "Delta Split"},
    ])

    # Page 1: only Alphas, limit 1
    r1 = client.get("/v1/plays", params={"limit": 1, "title": "Alpha"})
    b1 = r1.json()
    assert r1.status_code == 200
    assert [p["title"] for p in b1["data"]] == ["Alpha Cut"]
    # nextCursor should be the id of "Alpha Cut"
    assert b1["nextCursor"] == created[0]["id"]

    # Page 2: continue within same filter
    r2 = client.get("/v1/plays", params={"limit": 1, "title": "Alpha", "cursor": b1["nextCursor"]})
    b2 = r2.json()
    assert r2.status_code == 200
    assert [p["title"] for p in b2["data"]] == ["Alpha Spain"]
    # no more "Alpha..." items
    assert b2.get("nextCursor") in (None,)

def test_list_plays_filter_no_matches_returns_empty_200(client, seed_many_plays):
    seed_many_plays([
        {"title": "Alpha Cut"},
        {"title": "Bravo Ghost"},
    ])
    r = client.get("/v1/plays", params={"limit": 5, "title": "Zeta"})
    b = r.json()
    assert r.status_code == 200
    assert b["data"] == []
    assert b.get("nextCursor") in (None,)


def test_list_plays_cursor_at_end_returns_empty_page(client, seed_many_plays):
    created = seed_many_plays([
        {"title": "A1"},
        {"title": "A2"},
        {"title": "A3"},
    ])
    # cursor = last id → empty page, nextCursor null
    r = client.get("/v1/plays", params={"limit": 10, "cursor": created[-1]["id"]})
    b = r.json()
    assert r.status_code == 200
    assert [p["title"] for p in b["data"]] == []
    assert b.get("nextCursor") in (None,)


def test_list_plays_bad_cursor_returns_400(client, seed_many_plays):
    seed_many_plays([
        {"title": "Alpha Cut"},
        {"title": "Alpha Spain"},
    ])
    r = client.get("/v1/plays", params={"limit": 2, "cursor": "bogus-id"})
    assert r.status_code == 400
    body = r.json()
    # FastAPI default error envelope uses "detail"
    assert "detail" in body and "Invalid cursor" in body["detail"]


def test_list_plays_bad_cursor_with_filter_returns_400(client, seed_many_plays):
    created = seed_many_plays([
        {"title": "Alpha Cut"},
        {"title": "Bravo Ghost"},
    ])
    # Supply a real id that does NOT match the filter subset → invalid within the filtered view
    wrong_subset_cursor = created[1]["id"]  # "Bravo Ghost"
    r = client.get("/v1/plays", params={"limit": 2, "title": "Alpha", "cursor": wrong_subset_cursor})
    assert r.status_code == 400
    body = r.json()
    assert "detail" in body and "Invalid cursor" in body["detail"]
