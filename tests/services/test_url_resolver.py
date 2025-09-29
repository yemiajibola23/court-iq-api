import pytest
import importlib
import app.core.config as cfg
import app.services.url_resolver as resolver
from pathlib import Path
from typing import Callable

def test_public_video_url_from_cdn_base_and_key(set_env_and_reload):
    # Arrange
    set_env_and_reload(public_cdn="https://cdn.local", allow_local_preview="false", local_static_base=None)
    play = {"storage_key": "videos/abc.mp4"}
    
    assert cfg.PREVIEW_URL_BASE() == "https://cdn.local"
    
    # Act
    video_url, _ = resolver.build_public_urls(play)
    
    # Assert
    assert video_url == "https://cdn.local/videos/abc.mp4"
    
    
def test_local_path_allowed_maps_to_dev_static(media_root, make_play_from_media):
    # Arrange
    media = media_root(
        allow_local_preview="true",
        local_static_base="http://localhost:8000/static",
        public_cdn=None,
    )
    assert cfg.PREVIEW_URL_BASE() == "http://localhost:8000/static"

    _, play = make_play_from_media(media, "videos/abc.mp4", use_path=True)
    
    # Act
    video_url, _ = resolver.build_public_urls(play)
    
    # Assert
    assert video_url == "http://localhost:8000/static/videos/abc.mp4"
    
def test_local_path_disallowed_returns_null_video_url(media_root, make_play_from_media):
    # Arrange
    media = media_root(
        allow_local_preview="false",
        local_static_base="http://localhost:8000/static",
        public_cdn=None,
    )
    
    _, play = make_play_from_media(media, "videos/abc.mp4", use_path=True)
    video_url, _ = resolver.build_public_urls(play)
    
    assert cfg.PREVIEW_URL_BASE() is None
    
    # Act
    video_url, _ = resolver.build_public_urls(play)
    
    # Assert
    assert video_url is None
    
def test_thumbnail_placeholder_when_missing_cdn_env(set_env_and_reload):
    # Arrange
    set_env_and_reload(public_cdn="https://cdn.local", allow_local_preview="false")
    play = {"storage_key": "videos/abc.mp4"}
    
    assert cfg.PREVIEW_URL_BASE() == "https://cdn.local"

    # Act
    _, thumb_url = resolver.build_public_urls(play)
    
    # Assert
    assert thumb_url is not None
    assert thumb_url == cfg.THUMB_PLACEHOLDER_URL
    

def test_thumbnail_placeholder_when_missing_restricted_env(set_env_and_reload):
    # Arrange
    set_env_and_reload(allow_local_preview="false")
    play = {"storage_key": "videos/abc.mp4"}
    
    assert cfg.PREVIEW_URL_BASE() is None

    # Act
    _, thumb_url = resolver.build_public_urls(play)
    
    # Assert
    assert thumb_url is not None
    assert thumb_url == cfg.THUMB_PLACEHOLDER_URL
    
@pytest.mark.parametrize("base, rel, expected", [
     # trailing slash on base
        ("https://cdn.local/", "videos/abc.mp4", "https://cdn.local/videos/abc.mp4"),
        # leading slash on rel
        ("https://cdn.local", "/videos/abc.mp4", "https://cdn.local/videos/abc.mp4"),
        # both trailing+leading
        ("https://cdn.local/", "/videos/abc.mp4", "https://cdn.local/videos/abc.mp4"),
        # backslashes in rel (normalize)
        ("http://localhost:8000/static", r"videos\abc.mp4", "http://localhost:8000/static/videos/abc.mp4"),
        # empty rel → reject
        ("https://cdn.local", "", None),
        # absolute rel (http) → reject
        ("https://cdn.local", "http://evil/x", None),
        # absolute rel (HTTPS uppercase) → reject
        ("https://cdn.local", "HTTPS://evil/x", None),
        ("https://cdn.local", "HtTpS://evil/x", None),

])
def test_url_join_edge_cases(base, rel, expected):
    # Act
    result = resolver._url_join(base, rel) 
    
    if expected is None:
        assert result is None
    else:
        assert result == expected
        assert result is not None
        
        path_part = result.split("//", 1)[-1]
        assert "//" not in path_part
    
    
@pytest.mark.parametrize("relative_path_under_root, expected_tail", [
    ("videos/abc.mp4", "videos/abc.mp4"),
    ("videos/2024/abc.mp4", "videos/2024/abc.mp4"),
    (r"videos\abc.mp4", "videos/abc.mp4")
])
def test_local_preview_maps_paths_under_media_root(relative_path_under_root, expected_tail, media_root, make_play_from_media):
    # Arrange
    media = media_root(
        allow_local_preview="true", 
        local_static_base="http://localhost:8000/static", 
        public_cdn=None
    )
    
    assert cfg.PREVIEW_URL_BASE() == "http://localhost:8000/static"
    
    _, play = make_play_from_media(media, relative_path_under_root, use_path=True)

    # Act
    video_url, _ =resolver.build_public_urls(play)
    
    # Assert
    assert video_url == "http://localhost:8000/static/" + expected_tail
    assert video_url
    assert "//" not in video_url.split("//", 1)[-1]
    
@pytest.mark.parametrize("variant", [
    "sibling_dir",
    "traversal_resolves_outside",
    "other_media_tree"
])    
def test_local_preview_rejects_paths_outside_media_root(variant, media_root):
    # Arrange
    media = media_root(
        allow_local_preview="true", 
        local_static_base="http://localhost:8000/static", 
        public_cdn=None
    )
        
    assert cfg.PREVIEW_URL_BASE() == "http://localhost:8000/static"
        
    if variant == "sibling_dir":
        # MEDIA_ROOT = <tmp>/media; outside = <tmp>/other/abc.mp4
        outside = media.parent / "other" / "abc.mp4"
        outside.parent.mkdir(parents=True, exist_ok=True)
        outside.touch(exist_ok=True)

    elif variant == "traversal_resolves_outside":
        # Build a path that resolves outside MEDIA_ROOT via '..'
        candidate = media / ".." / "outside.mp4"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.touch(exist_ok=True)
        outside = candidate.resolve()

    elif variant == "other_media_tree":
        # MEDIA_ROOT stays <tmp>/media; file lives under <tmp>/mediaB/abc.mp4
        other = media.parent / "mediaB" / "abc.mp4"
        other.parent.mkdir(parents=True, exist_ok=True)
        other.touch(exist_ok=True)
        outside = other.resolve()

    else:
        pytest.fail(f"Unknown variant: {variant}")
        
    play = {"storage_path": outside.as_posix()}     
        
    # Act
    video_url, _ =resolver.build_public_urls(play)
    
    
    # Assert
    assert video_url == None
    
def test_local_preview_rejects_non_absolute_paths(media_root):
    media_root(allow_local_preview="true", local_static_base="http://localhost:8000/static", public_cdn=None)
    assert cfg.PREVIEW_URL_BASE() == "http://localhost:8000/static"

    play = {"storage_path": "videos/abc.mp4"}  # relative, not absolute
    video_url, _ = resolver.build_public_urls(play)
    assert video_url is None
