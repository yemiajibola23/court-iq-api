# tests/routers/test_plays_post_flags.py
import os
import uuid
import pytest

# --- Helpers ---------------------------------------------------------------

def set_flags(monkeypatch, *, allow_local: bool, media_root: str = "/tmp/media"):
    monkeypatch.setenv("ALLOW_LOCAL_VIDEO_PATHS", "true" if allow_local else "false")
    monkeypatch.setenv("MEDIA_ROOT", media_root)

# --- Baseline validation (https + allowed extensions + length) ------------

@pytest.mark.skip(reason="Planned Day 11: tighten schema (https only, ext set, len≤2048)")
def test_create_play_422_http_scheme_rejected(client, assert_422_field):
    payload = {"title": "Valid", "video_path": "http://example.com/clip.mp4"}
    res = client.post("/v1/plays", json=payload)
    assert_422_field(res, "video_path")

@pytest.mark.skip(reason="Planned Day 11: tighten schema (https only, ext set, len≤2048)")
def test_create_play_422_unsupported_extension_avi(client, assert_422_field):
    payload = {"title": "Valid", "video_path": "https://cdn.example.com/clip.AVI"}
    res = client.post("/v1/plays", json=payload)
    assert_422_field(res, "video_path")

@pytest.mark.skip(reason="Planned Day 11: length ≤ 2048")
def test_create_play_422_url_too_long(client, assert_422_field):
    long_path = "a" * 2050 + ".mp4"
    payload = {"title": "Valid", "video_path": f"https://cdn.example.com/{long_path}"}
    res = client.post("/v1/plays", json=payload)
    assert_422_field(res, "video_path")

@pytest.mark.skip(reason="Planned Day 11: case-insensitive extension check without mutating URL")
def test_create_play_201_allows_case_insensitive_extension(client):
    payload = {"title": "Valid", "video_path": "https://cdn.example.com/CLIP.MP4"}
    res = client.post("/v1/plays", json=payload)
    assert res.status_code in (200, 201)

# --- Dev override OFF (reject local paths) --------------------------------

@pytest.mark.skip(reason="Planned Day 12: enforce dev override flags OFF")
def test_create_play_422_file_scheme_rejected_when_override_off(client, assert_422_field, monkeypatch):
    set_flags(monkeypatch, allow_local=False)
    payload = {"title": "Valid", "video_path": "file:///Users/yemi/Vids/clip.mp4"}
    res = client.post("/v1/plays", json=payload)
    assert_422_field(res, "video_path")

@pytest.mark.skip(reason="Planned Day 12: enforce dev override flags OFF")
def test_create_play_422_relative_path_rejected_when_override_off(client, assert_422_field, monkeypatch):
    set_flags(monkeypatch, allow_local=False, media_root="/tmp/media")
    payload = {"title": "Valid", "video_path": "videos/clip.mp4"}
    res = client.post("/v1/plays", json=payload)
    assert_422_field(res, "video_path")

# --- Dev override ON (allow local paths with constraints) ------------------

@pytest.mark.skip(reason="Planned Day 12: allow file:// absolute path when override ON")
def test_create_play_201_file_scheme_allowed_when_override_on(client, monkeypatch):
    set_flags(monkeypatch, allow_local=True)
    payload = {"title": "Valid", "video_path": "file:///Users/yemi/Vids/clip.mp4"}
    res = client.post("/v1/plays", json=payload)
    assert res.status_code in (200, 201)
    assert "Location" in res.headers

@pytest.mark.skip(reason="Planned Day 12: allow relative path under MEDIA_ROOT when override ON")
def test_create_play_201_relative_under_media_root_when_override_on(client, monkeypatch, tmp_path):
    media_root = tmp_path / "media"
    media_root.mkdir()
    set_flags(monkeypatch, allow_local=True, media_root=str(media_root))
    payload = {"title": "Valid", "video_path": "videos/clip.mp4"}
    res = client.post("/v1/plays", json=payload)
    assert res.status_code in (200, 201)

@pytest.mark.skip(reason="Planned Day 12: prevent path traversal even when override ON")
def test_create_play_422_relative_path_traversal_blocked_when_override_on(client, assert_422_field, monkeypatch, tmp_path):
    media_root = tmp_path / "media"
    media_root.mkdir()
    set_flags(monkeypatch, allow_local=True, media_root=str(media_root))
    payload = {"title": "Valid", "video_path": "../outside/escape.mp4"}
    res = client.post("/v1/plays", json=payload)
    assert_422_field(res, "video_path")
