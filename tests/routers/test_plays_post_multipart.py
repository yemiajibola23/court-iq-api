
def test_post_422_neither_file_nor_url(client, assert_422_field):
    # Arrange
    payload = {"title": "valid"}
    
    # Act 
    res = client.post("/v1/plays", json=payload)
    
    # Assert 
    assert_422_field(res, "__root__", contains="either file or video_path is required")
    
    