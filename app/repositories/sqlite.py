from pathlib import Path
from app.models.play import Play
from app.repositories.plays_repo import PlaysRepository
from typing import Optional, List, Tuple
import sqlite3
from uuid import uuid4
from datetime import datetime
from uuid import UUID
class SQLitePlaysRepo(PlaysRepository):
    conn: sqlite3.Connection
    
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path), detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.conn.execute("PRAGMA foreign_keys=ON;")
             
    def _init_schema(self):
        sql = """
        CREATE TABLE IF NOT EXISTS plays (
        id         TEXT PRIMARY KEY,
        title      TEXT NOT NULL,
        video_path TEXT NOT NULL,
        thumbnail_path TEXT,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
        );

        CREATE INDEX IF NOT EXISTS idx_plays_title ON plays(title);
        """
        self.conn.executescript(sql)
        self.conn.commit()
    
    def _row_to_play(self, row: sqlite3.Row) -> Play:
        raw = row["created_at"]
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return Play(id=row["id"], title=row["title"], video_path=row["video_path"], created_at=dt, thumbnail_path=row["thumbnail_path"])
    
    def create_play(self, title: str, video_path: str) -> Play:
        id = str(uuid4())
        sql = "INSERT INTO plays (id, title, video_path, thumbnail_path) VALUES (?, ?, ?, NULL)"
        self.conn.execute(sql, (id, title, video_path))
        self.conn.commit()
        
        play = self.get_play(id)
        if not play:
            raise RuntimeError(f"Inserted play not found: {id}")
        
        return play
        
    def get_play(self, id: str) -> Optional[Play]:
        sql = "SELECT id, title, video_path, thumbnail_path, created_at FROM plays WHERE id=?"
        cursor = self.conn.execute(sql, (id,))
        row = cursor.fetchone()
        if row is None:
            return None
        
        return self._row_to_play(row)

    def list_plays(
        self,
        *,
        limit: int = 10,
        title_prefix: Optional[str] = None,
        before_dt: Optional[datetime] = None,
        before_id: Optional[UUID] = None,
    ) -> Tuple[List[Play], Optional[str]]:
        # WHERE clauses & params
        where: list[str] = []
        params: list = []

        # Case-insensitive, trimmed prefix
        if title_prefix:
            pfx = title_prefix.strip().lower()
            if pfx:
                where.append("LOWER(title) LIKE ?")
                params.append(pfx + "%")

        # Exclusive cutoff for pagination boundary
        # Assumes created_at stored as ISO 8601 text (UTC) and id as TEXT UUID
        if before_dt is not None and before_id is not None:
            where.append("(created_at, id) < (?, ?)")
            params.append(before_dt.isoformat())
            params.append(str(before_id))

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""

        # Newest-first, deterministic: created_at DESC, id DESC
        # Fetch limit+1 to compute next_cursor without extra COUNT
        sql = f"""
            SELECT id, title, video_path, thumbnail_path, created_at
            FROM plays
            {where_sql}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        """
        params.append(int(limit) + 1)

        rows = self.conn.execute(sql, params).fetchall()
        items: List[Play] = [self._row_to_play(r) for r in rows]

        # Page slice
        page = items[:limit]

        # Protocol wants a string cursor; simplest is the last page item's id
        # (If you later encode both created_at & id, do it here.)
        next_cursor: Optional[str] = page[-1].id if len(items) > limit else None
        
        return page, next_cursor

    
    def delete_play(self, id: str) -> bool: 
        sql = "DELETE FROM plays WHERE id=?"
        with self.conn:
            cursor = self.conn.execute(sql, (id,))
        
        return cursor.rowcount > 0        
    
    def clear(self) -> None:
        sql = "DELETE FROM plays"
        with self.conn:
            self.conn.execute(sql)