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
