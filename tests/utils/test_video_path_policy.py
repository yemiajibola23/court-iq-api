import pytest
from pathlib import Path
from app.utils.video_path_policy import validate_video_path
import os
import sys

ALLOWED_EXT_PATHS = {".mp4", ".mov", ".m4v", ".webm"}

def test_reject_flie_url_when_flag_off(tmp_path):
    media_path = tmp_path / "media"
    media_path.mkdir()
    
    with pytest.raises(ValueError) as e:
        validate_video_path("file://etc/passwd", allow_local=False, media_root=media_path)
        
    assert "local file paths are not allowed in this environment" in str(e.value)
    
    
def test_reject_relative_path_when_flag_off(tmp_path):
    media_path = tmp_path / "media"
    media_path.mkdir()
    
    with pytest.raises(ValueError) as e:
        validate_video_path("clips/foo.mp4", allow_local=False, media_root=media_path)
        
    assert "local file paths are not allowed in this environment" in str(e.value)
    
    
def test_accept_remote_https_with_supported_extensions(tmp_path):
    media_path = tmp_path / "media"
    media_path.mkdir()
    
    kind, value = validate_video_path("https://example.com/foo.mp4", allow_local=False, media_root=media_path)
    
    assert kind == "remote"
    assert value == "https://example.com/foo.mp4"
    
    
def test_reject_remote_https_with_bad_extensions(tmp_path):
    media_path = tmp_path / "media"
    media_path.mkdir()
    
    with pytest.raises(ValueError) as e:
        validate_video_path("https://example.com/readme.txt", allow_local=False, media_root=media_path)
    
    assert f"unsupported extension; allowed: {', '.join(sorted(ALLOWED_EXT_PATHS))}" in str(e.value)

def test_accepts_file_uri_under_media_root_when_flag_on(tmp_path):
    media_root = tmp_path / "media"
    (media_root / "ok").mkdir(parents=True)
    file_path = media_root / "ok" / "foo.mp4"
    file_path.touch()
    
    kind, value = validate_video_path(f"file://{file_path}", allow_local=True, media_root=media_root)
    
    assert kind == "local"
    assert Path(value) == file_path.resolve()
    
def test_accepts_relative_path_under_media_root_when_flag_on(tmp_path):
    media_root = tmp_path / "media"
    (media_root / "clips").mkdir(parents=True)
    file_path = media_root / "clips" / "foo.mov"
    file_path.touch()
    
    kind, value = validate_video_path(f"clips/foo.mov", allow_local=True, media_root=media_root)
    
    assert kind == "local"
    assert Path(value) == file_path.resolve()
    
def test_rejects_traversal_outside_media_root_when_flag_on(tmp_path):
    media_root = tmp_path / "media"
    media_root.mkdir()
    
    with pytest.raises(ValueError) as e:
        validate_video_path("../outside.mp4", allow_local=True, media_root=media_root)
        
    assert "path must be within MEDIA_ROOT" in str(e.value)

@pytest.mark.skipif(sys.platform.startswith("win"), reason="symlink perms flaky on Windows")   
def test_rejects_symlink_escape_when_flag_on(tmp_path):
    """
    Create a symlink inside media that points outside; validator should resolve realpath and reject.
    """
    media_root = tmp_path / "media"
    outside = tmp_path / "outside"
    (media_root / "linkdir").mkdir(parents=True)
    outside.mkdir()
    
    target = outside / "secrets.mp4"
    target.touch()
    
    link = media_root / "linkdir" / "secrets.mp4"
    os.symlink(target, link)
    
    with pytest.raises(ValueError) as e:
        validate_video_path("linkdir/secrets.mp4", allow_local=True, media_root=media_root)
        
    assert "path must be within MEDIA_ROOT" in str(e.value)