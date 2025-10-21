from uuid import uuid4, UUID
from typing import Optional, Dict, List, Tuple
from app.models.play import Play
from datetime import datetime, timezone
from app.repositories.plays_repo import PlaysRepository
import threading

_STORE: Dict[str, Play] = {}
class MemoryRepository(PlaysRepository):
    
    def __init__(self):
        self._items =  _STORE
        self._seq: dict[str, int] = {}
        self._next_seq = 0

    def _matches_prefix(self, title: str, prefix: Optional[str]) -> bool:
        """Case-insensitive, trimmed prefix match. None/'' => match all."""
        if not prefix:                 # None or ""
            return True
        return title.casefold().startswith(prefix.strip().casefold())

    def create_play(self, title: str, video_path: str, thumbnail_path: str | None=None) -> Play:
        with threading.RLock():
            play_id = str(uuid4())
            play = Play(
                id=play_id,
                title=title,
                video_path=video_path,
                thumbnail_path=thumbnail_path)
            self._items[play_id] = play
            self._seq[play_id] = self._next_seq
            self._next_seq += 1
    
            return play
    
    def get_play(self, id: str) -> Optional[Play]:
        with threading.RLock():
            return self._items.get(id)

    def list_plays(self, *, limit: int = 10, title_prefix: Optional[str] = None, before_dt: Optional[datetime]=None, before_id:Optional[UUID]=None) -> Tuple[List[Play], Optional[str]]:
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
         
        with threading.RLock():
            items: List[Play] = list(self._items.values())
        
        if title_prefix:
            pfx = title_prefix.strip().lower()
            items = [p for p in items if self._matches_prefix(p.title, pfx)]
            
        items.sort(key=lambda p: (p.created_at, self._seq.get(p.id, -1)),
                  reverse=True)
        
        if before_dt is not None and before_id is not None:
            cutoff_seq = self._seq.get(str(before_id), -1)
            items = [
                p for p in items
                if (p.created_at, self._seq.get(p.id, -1)) < (before_dt, cutoff_seq)
            ]
            
        slice_rows = items[: limit + 1]
        page = slice_rows[:limit]
        next_cursor = page[-1].id if len(slice_rows) > limit else None
        
        return page, next_cursor
            
    def delete_play(self, id: str) -> bool:
        with threading.RLock():
            removed = self._items.pop(id, None)
    
            return removed is not None

    def clear(self) -> None:
        """Remove all plays and reset insertion tracking."""
        with threading.RLock():
            self._items.clear()
            self._seq.clear()
            self._next_seq = 0
        