from uuid import uuid4, UUID
from typing import Optional, Dict, List, Tuple
from app.models.play import Play

# TECH_DEBT: TD1, TD8  — replace in-memory store with DB repo; add test-time reset/fixture to avoid cross-test pollution.
# TECH_DEBT: TD3       — add direct unit tests for repo methods (create/get).


_STORE: Dict[str, Play] = {}

def _matches_prefix(title: str, prefix: Optional[str]) -> bool:
    """Case-insensitive, trimmed prefix match. None/'' => match all."""
    if not prefix:                 # None or ""
        return True
    return title.casefold().startswith(prefix.strip().casefold())

def create(title: str, video_path: str) -> Play:
    play_id = str(uuid4())
    
    play = Play(play_id, title, video_path)
    
    _STORE[play_id] = play
    
    return play

def get(id: str) -> Optional[Play]:
    return _STORE.get(id)

def clear_store():
    _STORE.clear()


def list_plays(cursor: Optional[str], limit: int, title_prefix: Optional[str] = None) -> Tuple[List[Play], Optional[str]]:
    """Filter by title prefix, then paginate over stable insertion order.

    Cursor policy:
    - cursor must be an id present within the filtered view; otherwise ValueError('invalid_cursor')
    - results start strictly AFTER the cursor
    - next_cursor is the last id in the page iff more items remain
    """
    # 1) Keys are in insertion order in Python 3.7+
    keys = [k for k in _STORE if _matches_prefix(_STORE[k].title, title_prefix)]
    
    # Normalize limit
    lim = max(0, int(limit))
    
    # 2) Find start index strictly after the cursor
    if cursor is None:
        start_idx = 0
    else:
        try:
            start_idx = keys.index(cursor) + 1
        except ValueError:
            raise ValueError("invalid_cursor")
    
    # 3) Slice the page
    end_idx = start_idx + lim
    page_keys = keys[start_idx:end_idx]
    items = [ _STORE[k] for k in page_keys ]        
    
    # 4) Compute next cursor
    has_more = end_idx < len(keys)
    next_cursor = page_keys[-1] if (page_keys and has_more) else None
    
    return items, next_cursor

def delete(id: str) -> bool:
    removed = _STORE.pop(id, None)
    
    return removed is not None