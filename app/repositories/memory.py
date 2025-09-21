from uuid import uuid4, UUID
from typing import Optional, Dict, List, Tuple
from app.models.play import Play
from datetime import datetime, timezone

# TECH_DEBT: TD1, TD8  — replace in-memory store with DB repo; add test-time reset/fixture to avoid cross-test pollution.
# TECH_DEBT: TD3       — add direct unit tests for repo methods (create/get).

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
        play = Play(play_id, title, video_path, created_at=datetime.now(timezone.utc))
    
        self._items[play_id] = play
    
        return play
    
    def get_play(self, id: str) -> Optional[Play]:
        return self._items.get(id)

    def list_plays(self, 
                   *, 
                   limit: int = 10, 
                   title_prefix: Optional[str] = None, 
                   before_dt: Optional[datetime] = None, 
                   before_id: Optional[UUID] = None) -> Tuple[List[Play], bool]:
        """
        Return plays filtered by optional title prefix and paginated in a stable,
        deterministic order (newest first).

        Ordering
        -------
        Items are sorted by (created_at DESC, id DESC).

        Pagination semantics
        --------------------
        - If `before_dt` and `before_id` are provided, only items with
        (created_at, UUID(id)) strictly less than that tuple are returned.
        This makes the page boundary exclusive and prevents duplicates
        between pages.
        - At most `limit` items are returned.
        - The method returns a second boolean, `has_more`, indicating whether
        additional items exist after this page.

        Notes
        -----
        - Title filtering is a case-insensitive, trimmed, prefix match.
        - This repository does not encode/decode opaque cursor tokens. The
        router is responsible for mapping (created_at, id) <-> token.

        Args:
            limit: Maximum number of items to return.
            title_prefix: Optional case-insensitive prefix to filter titles.
            before_dt: Optional UTC datetime cutoff from the last item of the previous page.
            before_id: Optional UUID cutoff paired with `before_dt`.

        Returns:
            Tuple[List[Play], bool]: (items_on_page, has_more)
        """
         
        rows = self._items.values()
        
        if title_prefix is not None:
            q = title_prefix.strip().lower()
            if q:
                rows = [p for p in rows if p.title.strip().lower().startswith(q)]
            else:
                rows = list(rows)
        else:
            rows = list(rows)
            
        rows.sort(key=lambda p: (p.created_at, UUID(p.id)),
                  reverse=True)
        
        if before_dt is not None and before_id is not None:
            cutoff = (before_dt, before_id)
            rows = [
                p for p in rows
                if (p.created_at, UUID(p.id)) < cutoff
            ]
            
        slice_rows = rows[: limit + 1]
        has_more = len(slice_rows) > limit
        page = slice_rows[:limit]
        
        return page, has_more
            
    def delete_play(self, id: str) -> bool:
        removed = self._items.pop(id, None)
    
        return removed is not None

    def clear(self) -> None:
        self._items.clear()
        