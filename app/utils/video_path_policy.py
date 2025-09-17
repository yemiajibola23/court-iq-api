
from urllib.parse import urlsplit
from pathlib import Path
from typing import Literal, Union

ALLOWED_EXTS = {".mp4", ".mov", ".m4v", ".webm"}

RemoteResult = tuple[Literal["remote"], str]
LocalResult = tuple[Literal["local"], Path]
ReturnType = RemoteResult | LocalResult

def validate_video_path(raw: str, *, allow_local: bool, media_root) -> ReturnType:
    """
    Returns ("remote", url_str) or ("local", resolved_path)
    Raises ValueError with a precise message on invalid input.
    """
    if type(raw) is not str:
        raise ValueError("video_path must be a string")
    
    raw = raw.strip()
    if len(raw) > 2048:
        raise ValueError("video_path must be ≤ 2048 characters")
    
    parts = urlsplit(raw)
    
    # Remote
    if parts.scheme in { "https", "http" } and len(parts.netloc) > 0:
        ext = Path(parts.path).suffix.lower()
        if ext not in ALLOWED_EXTS:
            raise ValueError("unsupported extension; allowed: .m4v, .mov, .mp4, .webm")

        return ("remote", raw)
    
    # Local 
    if not allow_local:
        raise ValueError("local file paths are not allowed in this environment")
    
    raise NotImplementedError