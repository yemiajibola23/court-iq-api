import pytest
import uuid

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
    seed_many_plays([
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

def test_list_plays_sets_default_limit_of_10(client, seed_many_plays):
    seed_many_plays([{f"title": "Alpha Cut {i:02d}"} for i in range(12)])
    
    r1 = client.get("/v1/plays")
    assert r1.status_code == 200

    b1 = r1.json()
    assert len(b1["data"]) == 10
    assert b1["nextCursor"] is not None

    last_id_on_page = b1["data"][-1]["id"]
    assert b1["nextCursor"] == last_id_on_page

@pytest.mark.parametrize("limit", [0, -5])   
def test_list_limit_below_min_is_clamped_to_1(client, seed_many_plays, limit):
    seed_many_plays([{"title": f"Alpha Cut {i:02d}"} for i in range(5)])
    
    r = client.get(f"/v1/plays?limit={limit}")
    assert r.status_code == 200
    
    b = r.json()
    assert len(b["data"]) == 1
    assert b["nextCursor"] is not None
    
def test_list_limit_above_max_is_clamped_to_100(client, seed_many_plays):
    seed_many_plays([{"title": f"Alpha Cut {i:03d}"} for i in range(120)])

    r = client.get("/v1/plays?limit=9999")
    assert r.status_code == 200
    b = r.json()
    assert len(b["data"]) == 100
    assert b["nextCursor"] is not None


def test_list_plays_clamps_limit_high_to_100(client, seed_many_plays):
    # Seed 120 so a clamped=100 first page leaves 20 for the next page
    created = seed_many_plays([{"title": f"Alpha Cut {i}"} for i in range(120)])

    r1 = client.get("/v1/plays?limit=1000")  # should clamp to 100
    assert r1.status_code == 200
    b1 = r1.json()
    assert len(b1["data"]) == 100
    # When more exist, we expect a continuation token
    assert b1["nextCursor"] is not None

    # Follow the cursor and ensure the remainder (20) is returned
    cursor = b1["nextCursor"]
    # sanity: looks like a uuid-ish id
    uuid.UUID(cursor)
    r2 = client.get(f"/v1/plays?cursor={cursor}&limit=1000")
    assert r2.status_code == 200
    b2 = r2.json()
    assert len(b2["data"]) == 20
    assert b2["nextCursor"] is None

def test_list_plays_clamps_limit_low_to_1(client, seed_many_plays):
    seed_many_plays([{"title": f"Alpha Cut {i}"} for i in range(5)])

    # limit=0 → clamp up to 1
    r1 = client.get("/v1/plays?limit=0")
    assert r1.status_code == 200
    b1 = r1.json()
    assert len(b1["data"]) == 1
    assert b1["nextCursor"] is not None  # more items remain

    # negative also clamps to 1
    r2 = client.get("/v1/plays?limit=-25")
    assert r2.status_code == 200
    b2 = r2.json()
    assert len(b2["data"]) == 1
    assert b2["nextCursor"] is not None
    
def test_list_plays_has_more_returns_true_when_more_pages(client, seed_many_plays):
    seed_many_plays({"title": f"Alpha Cut {i:03d}"} for i in range(15))
    
    r = client.get("/v1/plays?limit=10")
    assert r.status_code == 200
    
    b = r.json()
    assert len(b["data"]) == 10
    assert b["nextCursor"] is not None 
    assert b["hasMore"] is True
    
def test_list_plays_has_more_returns_false_when_on_last_page(client, seed_many_plays):
    seed_many_plays({"title": f"Alpha Cut {i:03d}"} for i in range(15))
    
    r1 = client.get("/v1/plays?limit=10")
    assert r1.status_code == 200
    
    b1 = r1.json()
    assert len(b1["data"]) == 10
    nextCursor =b1["nextCursor"]
    
    r2 = client.get(f"/v1/plays?limit=10&cursor={nextCursor}")
    assert r2.status_code == 200
    
    b2 = r2.json()
    assert len(b2["data"]) == 5
    assert b2["nextCursor"] == None
    assert b2["hasMore"] == False

def test_list_has_more_respects_clamp_limit(client, seed_many_plays):
    seed_many_plays({"title": f"Alpha Cut {i:03d}"} for i in range(120))
    
    r = client.get("/v1/plays?limit=9999") # clamps to 100
    assert r.status_code == 200
    
    b = r.json()
    assert len(b["data"]) == 100
    assert b["nextCursor"] is not None 
    assert b["hasMore"] is True