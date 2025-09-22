import os
import pytest
from app.services.uploads import validate_and_save_upload
from app.utils.video_path_policy import ALLOWED_EXTS

@pytest.mark.anyio
async def test_validate_and_save_ok_mp4_calls_writer_and_returns_uri(fake_upload_factory):
    # Arrange
    size = b"\x00\x00\x00\x18"
    ftyp = b"ftyp"
    brand = b"isom"
    padding = b"\00" * 8
    body = os.urandom(20_000) # ~20 KB
    
    payload = size + ftyp + brand + padding + body
    upload = fake_upload_factory(payload, filename="clip.mp4")
    chunks: list[bytes] = []        
    
    def write_chunk(b: bytes) -> None:
        chunks.append(b)
    
    # Act
    result = await validate_and_save_upload(upload, writer=write_chunk, allowed_exts=ALLOWED_EXTS, chunk_size=4096)
    
    # Assert
    match result:
        case ("ok", uri):
            assert uri == "upload://clip.mp4"
        case ("error", field, msg):
            pytest.fail(f"unexpected error: {field} → {msg}")
        
    assert b"".join(chunks) == payload
    assert len(chunks) >= 2

@pytest.mark.anyio    
async def test_validate_and_save_rejects_unsupported_extension(fake_upload_factory):
    # Arrange
    size = b"\x00\x00\x00\x18"
    ftyp = b"ftyp"
    brand = b"isom"
    padding = b"\00" * 8
    body = os.urandom(20_000) # ~20 KB
    
    payload = size + ftyp + brand + padding + body
    upload = fake_upload_factory(payload, filename="clip.avi")
    chunks: list[bytes] = []        
    
    def write_chunk(b: bytes) -> None:
        chunks.append(b)
    
    # Act
    result = await validate_and_save_upload(upload, writer=write_chunk, allowed_exts=ALLOWED_EXTS)
  
    # Assert
    match result:
        case ("ok", _):
            pytest.fail(f"Expected failure but succeeded.")
        case (tag, field, msg):
            assert field == "file"
            assert msg == "unsupported extension; allowed: .m4v, .mov, .mp4, .webm"
            
    assert chunks == []
    
@pytest.mark.anyio
async def test_validate_and_save_rejects_magic_mismatch(fake_upload_factory):
    # Arrange
    payload = b"\x1A\x45\xDF\xA3" + b"\x00"*32
    upload = fake_upload_factory(payload, filename="clip.mp4")
    
    chunks: list[bytes] = []        
    
    def write_chunk(b: bytes) -> None:
        chunks.append(b)
    
    # Act
    result = await validate_and_save_upload(upload, writer=write_chunk, allowed_exts=ALLOWED_EXTS)
    
    # Assert
    assert result[0] == "error"
    
    tag, field, msg = result
    
    assert field == "file"
    assert msg == "file content does not match extension"
    assert chunks == []