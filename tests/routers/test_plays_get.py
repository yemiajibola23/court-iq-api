def test_get_play_returns_404_when_id_doesnt_exist(client):
    fake_id="00000000-0000-0000-0000-000000000000"
    
    res = client.get(f"/v1/plays/{fake_id}")
    
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Play not found"
    