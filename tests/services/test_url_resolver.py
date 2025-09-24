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