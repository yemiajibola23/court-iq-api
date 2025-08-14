import pytest
import uuid

# TECH_DEBT: TD9 — assert per-field 422 arrays for all validation failures.

def test_create_play_ok_https_mp4_returns_201_and_location_header(client):
    """
    Happy path:
      - title: non-empty
      - video_path: https URL ending with .mp4
    Expect:
      - 201 Created
      - 'Location' header set to /v1/plays/{id}
    """
    payload = {"title": "Drop vs. Spain PnR", "video_path":"https://example.com/clip.mp4"}
    res = client.post("/v1/plays", json=payload)
    
    assert res.status_code == 201
    
    data = res.json()
    assert "playId" in data
    # Validate UUID-ish value (FastAPI serializes UUID -> string)
    uuid_val = data["playId"]
    uuid.UUID(uuid_val)
    
    # Location header
    assert "Location" in res.headers
    location = res.headers["Location"]
    assert location.startswith("/v1/plays/")

    # The id in Location should equal the JSON playId
    loc_id = location.rsplit("/", 1)[-1]
    assert loc_id == uuid_val

def test_create_play_422_empty_title(client, assert_422_field):
    """Empty/whitespace-only title → 422.title"""
    payload = {"title": "  ", "video_path": "https://example.com/clip.mp4"}
    res = client.post("/v1/plays", json=payload)
    
    assert_422_field(res, "title")
    
def test_create_play_422_missing_title(client, assert_422_field):
    """Missing 'title' field → 422.title"""
    payload = {"video_path": "https://example.com/clip.mp4"}  # title omitted
    res = client.post("/v1/plays", json=payload)
   
    assert_422_field(res, "title")
    
def test_create_play_422_missing_video_path(client, assert_422_field):
    """Missing 'video_path' field → 422.video_path"""
    payload = {"title": "Drop vs. Spain PnR"}  # video_path omitted
    res = client.post("/v1/plays", json=payload)
   
    assert_422_field(res, "video_path")

def test_create_play_422_ftp_scheme_rejected(client, assert_422_field):
    """video_path uses ftp:// → 422.video_path"""
    payload = {"title": "Valid", "video_path": "ftp://server/clip.mp4"}
    res = client.post("/v1/plays", json=payload)
    
    assert_422_field(res, "video_path")

@pytest.mark.skip(reason="planned Day 12: invalid types on upload")
def test_create_play_422_unsupported_extension_avi(): ...

@pytest.mark.skip(reason="planned Day 11: local paths gated by ALLOW_LOCAL_VIDEO_PATHS=false")
def test_create_play_422_local_file_path_rejected_when_override_off(): ...

@pytest.mark.skip(reason="planned Day 11: relative paths gated by ALLOW_LOCAL_VIDEO_PATHS=false")
def test_create_play_422_relative_path_rejected_when_override_off(): ...

@pytest.mark.skip(reason="planned Day 11/12: file:// allowed only when override true (+ type checks)")
def test_create_play_ok_file_scheme_allowed_with_override(): ...

@pytest.mark.skip(reason="planned Day 11: relative under MEDIA_ROOT allowed when override true")
def test_create_play_ok_relative_under_media_root_with_override(): ...

def test_create_play_trims_inputs_before_validation(client):
    """Leading/trailing whitespace is trimmed before rules apply."""
    payload = {"title": "  Spain   PnR  ", 
               "video_path": "https://example.com/clip.mp4  ",
               }
    res = client.post("/v1/plays", json=payload)
    assert res.status_code == 201
    location = res.headers["Location"]
    assert location.startswith("/v1/plays/")
    
    data = res.json()
    assert "playId" in data
    
    loc_id = location.rsplit("/", 1)[-1]
    assert data["playId"] == loc_id
 
