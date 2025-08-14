from uuid import uuid4
from typing import Optional, Dict
from app.models.play import Play

# TECH_DEBT: TD1, TD8  — replace in-memory store with DB repo; add test-time reset/fixture to avoid cross-test pollution.
# TECH_DEBT: TD3       — add direct unit tests for repo methods (create/get).


_STORE: Dict[str, Play] = {}

def create(title: str, video_path: str) -> Play:
    play_id = str(uuid4())
    
    play = Play(play_id, title, video_path)
    
    _STORE[play_id] = play
    
    return play

def get(id: str) -> Optional[Play]:
    return _STORE.get(id)