import pytest
import importlib
import app.core.config as cfg
import app.services.url_resolver as resolver

def test_public_video_url_from_cdn_base_and_key(monkeypatch):
    # Arrange
    monkeypatch.setenv("PUBLIC_CDN_BASE", "https://cdn.local")
    monkeypatch.setenv("ALLOW_LOCAL_PREVIEW", "false")
    monkeypatch.delenv("LOCAL_STATIC_BASE", raising=False)
    
    importlib.reload(cfg)
    importlib.reload(resolver)
    
    play = {"storage_key": "videos/abc.mp4"}
    
    # Act
    video_url, _ = resolver.build_public_urls(play)
    
    # Assert
    assert video_url == "https://cdn.local/videos/abc.mp4"