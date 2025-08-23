from pathlib import Path
from app.models.play import Play
from app.repositories.plays_repo import PlaysRepository
from typing import Optional, List, Tuple

class SQLitePlaysRepo():
    path: Path
    
    def __init__(self, path):
        self.path = path
        
    def create_play(self, title: str, video_path: str) -> Play:
        raise NotImplementedError

    def get_play(self, id: str) -> Optional[Play]:
        raise NotImplementedError
    
    def list_plays(self, *, cursor: Optional[str] = None, limit: int = 10, title_prefix: Optional[str] = None) -> Tuple[List[Play], Optional[str]]:
        raise NotImplementedError
    
    def delete_play(self, id: str) -> bool: 
        raise NotImplementedError
    