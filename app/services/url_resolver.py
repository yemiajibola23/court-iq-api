import app.core.config as cfg
from typing import Optional, Tuple
from pathlib import Path

def _url_join(base: str, rel: str) -> Optional[str]:
    """
    join base + relative, avoid //, reject absolute rel/schemes, return Optional[str]
    """
    base_norm = base.strip().rstrip('/')
    rel_norm = rel.strip().replace('\\', '/').lstrip('/')
    
    if not rel_norm or not base_norm or rel_norm.lower().startswith("http://") or rel_norm.lower().startswith("https://"):
        return None
    
    return f'{base_norm}/{rel_norm}'

def _relative_under_media_root(storage_path: Optional[str]) -> Optional[str]:
    """
    If `storage_path` is an absolute path inside MEDIA_ROOT, return its POSIX
    relative path (e.g., 'videos/abc.mp4'); otherwise return None.
    """
    if storage_path is None:
        return None
    
    p = Path(storage_path)
    if not p.is_absolute():
        return None
    
    root = cfg.MEDIA_ROOT.resolve()
    try:
        rel_path = p.expanduser().resolve().relative_to(root).as_posix()
    except ValueError:
        return None
    
    return rel_path or None
        
def build_public_urls(play: dict) -> Tuple[Optional[str], Optional[str]]:
    storage_key = play.get("storage_key") or play.get("storageKey")
    storage_path = play.get("storage_path") or play.get("storagePath")
    
    base = cfg.PREVIEW_URL_BASE()
    base_norm = base.rstrip("/") if base else None
    local_norm = cfg.LOCAL_STATIC_BASE.rstrip("/") if cfg.LOCAL_STATIC_BASE else None
    is_local_base = bool(base_norm and local_norm and base_norm == local_norm)
    thumbnail_url = cfg.THUMB_PLACEHOLDER_URL    

    video_url = None
    if not base:
        return (None, thumbnail_url)
    
    if is_local_base is True:
        if storage_path:
            relative = _relative_under_media_root(storage_path)
            if relative:
                video_url = _url_join(base, relative)
    else:
        if storage_key:
            video_url = _url_join(base, storage_key)
        elif storage_path:
            relative = _relative_under_media_root(storage_path)
            if relative:
                video_url = _url_join(base, relative)
        
    return video_url, thumbnail_url