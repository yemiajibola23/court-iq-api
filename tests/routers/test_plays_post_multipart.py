
from uuid import uuid4
from types import SimpleNamespace
from app.repositories.memory import MemoryRepository
import json

def test_post_422_neither_file_nor_url(client, assert_422_field):
    # Arrange
    payload = {"title": "valid"}
    
    # Act 
    res = client.post("/v1/plays", json=payload)
    
    # Assert 
    assert_422_field(res, "video_path")
    
def test_post_multipart_422_neither_file_nor_url(client, assert_422_field):
     # Arrange
    payload = {"title": "valid"}
    data = json.dumps(payload).encode()
    files = {"title" : (None, "valid")}
    
    # Act 
    res = client.post("/v1/plays", files=files)
    
    # Assert
    assert_422_field(res, "__root__", contains="either file or video_path is required")
    
def test_post_422_both_file_and_url(client, assert_422_field):
    # Arrange
    data = { "title": " valid", "video_path": "https://cdn.example.com/clip.mp4" }
    content = b"00"
    files = {"file": ("clip.mp4", content, "video/mp4")}
    
    # Act
    res = client.post("/v1/plays", data=data, files=files)
    
    # Assert
    assert_422_field(res, "__root__", contains="provide either file or video_path, not both")
    
def test_post_multipart_201_mp4_ok(client, assert_201_field):
    # Arrange
    size = b"\x00\x00\x00\x18"
    ftyp = b"ftyp"
    brand = b"isom"
    padding = b"0000"
    data = {"title": "valid"} # no video_path
    files = {"file": ("clip.mp4", size + ftyp + brand + padding, "video/mp4")} 
    
    # Act
    res = client.post("/v1/plays", data=data, files=files)
    
    # Assert
    assert_201_field(res)
    
def test_post_multipart_422_invalid_extension(client, assert_422_field):
    # Arrange
    data = {"title": "valid"}
    files = {"file": ("clip.avi", b"00", "video/x-msvideo")}
    
    # Act
    res = client.post("/v1/plays", data=data, files=files)
    
    # Assert
    assert_422_field(res, "file", contains="unsupported extension; allowed: .m4v, .mov, .mp4, .webm")
    
def test_post_multipart_422_magic_mismatch(client, assert_422_field):
    # Arrange
    data = {"title": "valid"}
    bad_bytes = b"\x1A\x45\xDF\xA3" + b"0"*32
    files = {"file": ("clip.mp4",bad_bytes, "video/mp4")} 
    
    # Act
    res = client.post("/v1/plays", data=data, files=files)
    
    # Assert
    assert_422_field(res, "file", contains="file content does not match extension")
    
def test_multipart_201_uses_service_uri(monkeypatch, client, assert_201_field):
    # Arrange 
    seen = {}
    
    async def fake_validate(upload, *, writer, allowed_exts, chunk_size=8192):
        return ("ok", "upload://mock.mp4")
    monkeypatch.setattr("app.routers.plays.validate_and_save_upload", fake_validate, raising=True)
    
    def fake_create(self, *, title: str, video_path: str) -> SimpleNamespace:
            seen["title"] = title
            seen["video_path"] = video_path
            
            return SimpleNamespace(id=str(uuid4()))
    monkeypatch.setattr(MemoryRepository, "create_play", fake_create, raising=True)
    
    data = {"title": "valid"}
    files = {"file": ("clip.mp4", b"\x00\x00\x00\x18ftypisom0000", "video/mp4")}
    
    # Act
    res = client.post("/v1/plays", data=data, files=files)

    # Assert
    assert_201_field(res)
    assert seen["title"] == "valid"
    assert seen["video_path"] == "upload://mock.mp4"
    
def test_multipart_422_maps_service_error(monkeypatch, client, assert_422_field):
    # Arrange
    async def fake_validate(upload, *, writer, allowed_exts, chunk_size=8192):
        return ("error", "file", "file content does not match extension")
    monkeypatch.setattr("app.routers.plays.validate_and_save_upload", fake_validate, raising=True)
    
    def boom(*args, **kwargs):
        raise AssertionError("create_play should not be called on service error")
    monkeypatch.setattr(MemoryRepository, "create_play", boom, raising=True)

    data = {"title": "valid"}
    files = {"file": ("clip.mp4", b"anything", "video/mp4")}
    
    # Act
    res = client.post("/v1/plays", data=data, files=files)
    
    # Assert 
    assert_422_field(res, "file", "file content does not match extension")