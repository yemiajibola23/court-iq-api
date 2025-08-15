# tests/routers/test_plays_delete.py
from typing import List, Dict
from uuid import uuid4

def test_delete_play_204_on_success(client):
    # arrange: create a play using POST /v1/plays and capture its id
    payload = {"title": "Test Play 1", "video_path": "https://example.com/clip.mp4"}
    create_res = client.post("/v1/plays",json= payload)
    assert create_res.status_code == 201, create_res.text
    
    location = create_res.headers.get("Location")
    play_id = create_res.json()["playId"]
    assert location and location.startswith("/v1/plays/"), f"Missing Location header: {create_res.headers}"
    assert location.rsplit("/", 1)[-1] == str(play_id)
   
    # act: send DELETE /v1/plays/{id} using the captured id
    delete_res = client.delete(f"/v1/plays/{play_id}")
    print("DELETE error payload:", delete_res.text)

    # assert: response status == 204
    assert delete_res.status_code == 204
    # assert: response body is empty (allow "", "null", or "{}" if your stack does that)
    assert delete_res.text in ("", "null", "{}") or delete_res.content in (b"",)

def test_get_after_delete_returns_404(client):
    # arrange: create a play, capture its UUID
    payload = {"title": "Test Play 1", "video_path": "https://example.com/clip.mp4"}
    create_res = client.post("/v1/plays",json= payload)
    assert create_res.status_code == 201, create_res.text
    
    location = create_res.headers.get("Location")
    play_id = create_res.json()["playId"]
    assert location and location.startswith("/v1/plays/"), f"Missing Location header: {create_res.headers}"
    assert location.rsplit("/", 1)[-1] == str(play_id)
    
    # act: delete it
    delete_res = client.delete(f"/v1/plays/{play_id}")

    # assert: delete returns 204
    assert delete_res.status_code == 204
    
    # act: GET the same id
    get_res = client.get(f"/v1/plays/{play_id}")
    
    # assert: GET returns 404
    assert get_res.status_code == 404
    
def test_list_no_longer_includes_deleted_id(client, seed_many_plays):
        # arrange: create three plays, capture their ids
        seed_many_plays([
            {"title": "Spain PnR"}, 
            {"title": "Drop Coverage"}, 
            {"title": "Zoom"},
        ])
        
        # sanity: GET /v1/plays shows all three ids
        list_res = client.get("/v1/plays")
        assert list_res.status_code == 200
        json_data = list_res.json()
        print("LIST JSON:", json_data)

        items = json_data["data"] if isinstance(json_data, dict) and "data" in json_data else json_data
        list_ids = [it.get("id") for it in items]
        before_ids = set(list_ids)
        assert len(list_ids) == 3
        
        # act: DELETE the middle one
        middle_id = list_ids[1]
        delete_res = client.delete(f"/v1/plays/{middle_id}")
        
        # assert: DELETE returned 204
        assert delete_res.status_code == 204
        
        # act: GET /v1/plays
        new_list_res = client.get("/v1/plays")
        new_json = new_list_res.json()
        new_items = new_json["data"] if isinstance(new_json, dict) and "data" in new_json else new_json    
        new_list_ids = [it.get("id") for it in new_items]
        after_ids = set(new_list_ids)

        # assert: deleted id is NOT present
        assert middle_id not in new_list_ids
        
        # assert: the other two ids ARE present
        assert after_ids == before_ids - {middle_id}
