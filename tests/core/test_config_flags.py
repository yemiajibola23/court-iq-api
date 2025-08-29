
import importlib
from pathlib import Path
import pytest
from app.core.config import config

def _reload_config(monkeypatch, **env):
    """
    Helper: clear known flags, set any provided values, then reload app.config
    so it re-reads environment variables on import.
    """
    
    # Clear first
    for key in ("ALLOW_LOCAL_VIDEO_PATHS", "MEDIA_ROOT"):
        if key not in env:
            monkeypatch.delenv(key, raising=False)
            
    # Apply overrides for this test
    for k,v in env.items():
        monkeypatch.setenv(k, str(v))
    
    return importlib.reload(config)

def test_default_flags_are_secure(monkeypatch):
    """
    With no env vars, we want the secure posture:
    - ALLOW_LOCAL_VIDEO_PATHS == False
    - MEDIA_ROOT is an absolute path that resolves to ./media
    """
    
    config = _reload_config(monkeypatch)
    
    assert config.ALLOW_LOCAL_VIDEO_PATHS is False
    assert isinstance(config.MEDIA_ROOT, Path)
    assert config.MEDIA_ROOT.is_absolute()
    assert config.MEDIA_ROOT == (Path("./media").resolve())
    
    
def test_env_overrides_for_flags(monkeypatch, tmp_path):
    """
    When env vars are set, they should override defaults:
    - ALLOW_LOCAL_VIDEO_PATHS from "true"/"false"
    - MEDIA_ROOT to a given absolute/relative path (resolved)
    """
    # Make a temp directory to stand in for MEDIA_ROOT
    desired_media = tm
    