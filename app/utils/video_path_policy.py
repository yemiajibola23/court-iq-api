
from urllib.parse import urlsplit, unquote
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
    if not isinstance(raw, str):
        raise ValueError("video_path must be a string")
    
    raw = raw.strip()
    if len(raw) > 2048:
        raise ValueError("video_path must be ≤ 2048 characters")
    
    parts = urlsplit(raw)
    allowed_txt = ", ".join(sorted(ALLOWED_EXTS))
    
    # Remote
    if parts.scheme in { "https", "http" } and parts.netloc:
        ext = Path(parts.path).suffix.lower()
        if ext not in ALLOWED_EXTS:
            raise ValueError(f"unsupported extension; allowed: {allowed_txt}")

        return ("remote", raw)
    
    # Local 
    if not allow_local:
        raise ValueError("local file paths are not allowed in this environment")
    else:
        root = Path(media_root).expanduser().resolve()
        if parts.scheme == "file":
            raw_fs_path = unquote(parts.path)
            candidate = Path(raw_fs_path)
        elif parts.scheme == "":
            p = Path(raw)
            if p.is_absolute():
                candidate = p
            else:
                candidate = root / p
        else:
            raise ValueError("local file paths are not allowed in this environment")

        candidate = candidate.expanduser().resolve(strict=False)
        
        ext = candidate.suffix.lower()
        if ext not in ALLOWED_EXTS:
            raise ValueError(f"unsupported extension; allowed: {allowed_txt}")
        
        if not candidate.is_relative_to(root):
            raise ValueError("path must be within MEDIA_ROOT")

        return ("local", candidate)