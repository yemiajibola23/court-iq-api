import os
import pytest
from app.services.uploads import save_upload

@pytest.mark.anyio
async def test_save_upload_streams_in_fixed_chunks(fake_upload_factory):
    # Arrange
    payload = os.urandom(20_000) # ~20 KB
    upload = fake_upload_factory(payload)
    chunks: list[bytes] = []        
    
    def write_chunk(b: bytes) -> None:
        chunks.append(b)
    
    # Act
    chunk_size = 8192
    url = await save_upload(upload=upload, writer=write_chunk, chunk_size=chunk_size)
    
    # Assert
    assert len(chunks) >= 2
    assert all(len(c) == 8192 for c in chunks[:-1])
    assert 0 < len(chunks[-1]) <= 8192
    assert b"".join(chunks) == payload
    assert url.startswith("upload://")