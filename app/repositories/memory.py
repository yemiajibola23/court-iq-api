from uuid import uuid4, UUID
from typing import Optional, Dict, List, Tuple
from app.models.play import Play
from datetime import datetime, timezone

# TECH_DEBT: TD1, TD8  — replace in-memory store with DB repo; add test-time reset/fixture to avoid cross-test pollution.
# TECH_DEBT: TD3       — add direct unit tests for repo methods (create/get).

def _utc_iso() -> str:
    # e.g. 2025-08-23T17:03:12.345678Z
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

_STORE: Dict[str, Play] = {}
class MemoryRepository:
    
    def __init__(self):
        self._items =  _STORE

    def _matches_prefix(self, title: str, prefix: Optional[str]) -> bool:
        """Case-insensitive, trimmed prefix match. None/'' => match all."""
        if not prefix:                 # None or ""
            return True
        return title.casefold().startswith(prefix.strip().casefold())

    def clear_store(self):
        self._items.clear()

    def create_play(self, title: str, video_path: str) -> Play:
        play_id = str(uuid4())
        play = Play(play_id, title, video_path, created_at=_utc_iso())
    
        self._items[play_id] = play
    
        return play
    
    def get_play(self, id: str) -> Optional[Play]:
        return self._items.get(id)

    def list_plays(self, *, cursor: Optional[str] = None, limit: int = 10, title_prefix: Optional[str] = None) -> Tuple[List[Play], Optional[str]]:
        """Filter by title prefix, then paginate over stable insertion order.

        Cursor policy:
        - cursor must be an id present within the filtered view; otherwise ValueError('invalid_cursor')
        - results start strictly AFTER the cursor
        - next_cursor is the last id in the page iff more items remain
        """
        # 1) Keys are in insertion order in Python 3.7+
        keys = [k for k in self._items if self._matches_prefix(self._items[k].title, title_prefix)]
    
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
        items = [ self._items[k] for k in page_keys ]        
    
        # 4) Compute next cursor
        has_more = end_idx < len(keys)
        next_cursor = page_keys[-1] if (page_keys and has_more) else None
    
        return items, next_cursor

    def delete_play(self, id: str) -> bool:
        removed = self._items.pop(id, None)
    
        return removed is not None

    def clear(self) -> None:
        self._items.clear()
        