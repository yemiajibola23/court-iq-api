from pathlib import Path
from app.models.play import Play
from app.repositories.plays_repo import PlaysRepository
from typing import Optional, List, Tuple
import sqlite3
from uuid import uuid4
class SQLitePlaysRepo():
    conn: sqlite3.Connection
    
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path), detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        
    def _init_schema(self):
        sql = """
        CREATE TABLE IF NOT EXISTS plays (
        id         TEXT PRIMARY KEY,
        title      TEXT NOT NULL,
        video_path TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
        );

        CREATE INDEX IF NOT EXISTS idx_plays_title ON plays(title);
        """
        self.conn.executescript(sql)
        self.conn.commit()
    
    def _row_to_play(self, row: sqlite3.Row) -> Play:
        return Play(id=row["id"], title=row["title"], video_path=row["video_path"], created_at=row["created_at"])
    
    def create_play(self, title: str, video_path: str) -> Play:
        id = str(uuid4())
        sql = "INSERT INTO plays (id, title, video_path) VALUES (?, ?, ?)"
        self.conn.execute(sql, (id, title, video_path))
        self.conn.commit()
        
        play = self.get_play(id)
        if not play:
            raise RuntimeError(f"Inserted play not found: {id}")
        
        return play
        
    def get_play(self, id: str) -> Optional[Play]:
        sql = "SELECT id, title, video_path, created_at FROM plays WHERE id=?"
        cursor = self.conn.execute(sql, (id,))
        row = cursor.fetchone()
        if row is None:
            return None
        
        return self._row_to_play(row)
    
    def list_plays(self, *, cursor: Optional[str] = None, limit: int = 10, title_prefix: Optional[str] = None) -> Tuple[List[Play], Optional[str]]:
        raise NotImplementedError
    
    def delete_play(self, id: str) -> bool: 
        raise NotImplementedError
    
    def clear(self) -> None:
        raise NotImplementedError