from typing import Protocol, Callable, Awaitable, Literal, Union
from inspect import isawaitable
from pathlib import Path

class UploadLike(Protocol):
    filename: str | None
    
    async def read(self, size: int) -> bytes: ...
    async def seek(self, offset: int) -> None: ...


async def save_upload(upload: UploadLike, writer: Callable[[bytes], None] | Callable[[bytes], Awaitable[None]], chunk_size: int = 8192) -> str:
    await upload.seek(0)
    
    if chunk_size <= 0:
        chunk_size = 8192
    
    while True:
        chunk = await upload.read(chunk_size)
        if not chunk: break
       
        result = writer(chunk)
        if isawaitable(result):
            await result
    
    name = (upload.filename or "").strip() or "unnamed"
    
    return "upload://" + name

Ok =tuple[Literal["ok"], str]
Err = tuple[Literal["error"], str, str]
async def validate_and_save_upload(upload: UploadLike, writer: Callable[[bytes], None] | Callable[[bytes], Awaitable[None]], allowed_exts={".mp4", ".mov", ".m4v", ".webm"}, chunk_size: int = 8192) -> Ok | Err:
    name = (upload.filename or "").strip()
    if len(name) <= 0:
        return ("error", "__root__", "filename required")
    
    ext = Path(name).suffix.lower()
    if ext not in allowed_exts:
        return ("error", "file", f"unsupported extension; allowed: {', '.join(sorted(allowed_exts))}")
    
    head = await upload.read(16)
    await upload.seek(0)
    
    mismatch = False
    if ext == ".webm":
        if not head.startswith(b"\x1A\x45\xDF\xA3"):
            mismatch = True     
    else:
        if len(head) < 8 or head[4:8] != b"ftyp":
            mismatch = True
            
    if mismatch:
        return ("error", "file", "file content does not match extension")
    
    uri = await save_upload(upload, writer, chunk_size)
    
    return ("ok", uri)