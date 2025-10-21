from pathlib import Path
from app.models.play import Play
import uuid as _uuid
from datetime import datetime
from typing import Dict
from app.repositories.sqlite import SQLitePlaysRepo
from app.repositories.plays_repo import PlaysRepository

def test_sqlite_repo_create_and_get_ok(tmp_path: Path):
    # Arrange
    db_path = tmp_path / "db.sqlite"
    repo = SQLitePlaysRepo(db_path)
    assert isinstance(repo, PlaysRepository)
    
    title = "Spain PnR"
    video_path = "https://example.com/clip.mp4"
    
    # Act
    created = repo.create_play(title, video_path)
    assert(isinstance(created, Play))
    play_id = created.id
    
    # Assert
    fetched = repo.get_play(play_id)
    assert isinstance(fetched, Play)
    assert fetched.title == title
    assert fetched.video_path == video_path
    
    _ = _uuid.UUID(play_id)
    
    assert isinstance(fetched.created_at, datetime)
    assert fetched.created_at.tzinfo is not None  # is timezone aware
    
def test_sqlite_repo_list_prefix_filter_case_insensitive(tmp_path: Path):
    # Arrange
    db_path = tmp_path / "db.sqlite"
    repo = SQLitePlaysRepo(db_path)
    # assert isinstance(repo, PlaysRepository)
    
    video_path = "https://example.com/clip.mp4"
    plays_dict: Dict[str, str] = {}
    titles: set = {"Alpha Cut", "alpha Spain", "ALPHAbet Soup", "Bravo"}
    
    for name in titles:
        play = repo.create_play(name, video_path)
        plays_dict[play.title] = play.id

    # Act
    items, next_cursor = repo.list_plays(limit=50, title_prefix= "  alpha  ")
    
    # Assert
    assert len(items) == 3
    assert next_cursor is None
    assert set([p.title for p in items]) == {"Alpha Cut", "alpha Spain", "ALPHAbet Soup"}
    assert all(p.title.lower().startswith("alpha") for p in items)
    
    ids = [p.id for p in items]
    # assert ids == sorted(ids)
    
def test_sqlite_repo_list_pagination_with_cursor(tmp_path: Path):
    # Arrange
    db_path = tmp_path / "db.sqlite"
    repo = SQLitePlaysRepo(db_path)
    # assert isinstance(repo, PlaysRepository)
    
    video_path = "https://example.com/clip.mp4"
    plays_dict: Dict[str, str] = {}
    titles = ["Alpha Cut", "alpha Spain", "ALPHAbet Soup", "Bravo"]
    
    for name in titles:
        p = repo.create_play(name, video_path)
        plays_dict[p.title] = p.id
    
    expected_alpha_ids = sorted([
        plays_dict["Alpha Cut"],
        plays_dict["alpha Spain"],
        plays_dict["ALPHAbet Soup"],        
    ])
        
    # Act
    items1, cur = repo.list_plays(limit=2, title_prefix="alpha")
    assert len(items1) <= 2
    
    if items1:
        last = items1[-1]
        last_dt = last.created_at
        last_uuid = _uuid.UUID(last.id)
        items2, cur2 = repo.list_plays(limit=2, title_prefix="alpha", before_dt=last_dt, before_id=last_uuid)
    else:
        items2, cur2 = [], None
    
    # Assert
    assert len(items1) == 2
    assert len(items2) == 1
    assert isinstance(cur, (str, type(None)))
    
    assert cur == (items1[-1].id if len(items1) == 2 else None)
    assert cur2 is None
    
    assert all(p.title.lower().startswith("alpha") for p in items1 + items2)
    
    def key(play: Play):
        return (play.created_at, play.id)
    
    if items2:
        k1 = key(items1[-1])
        k2 = key(items2[0])
        assert k2 < k1  # descending order

def test_sqlite_repo_delete_ok_and_404(tmp_path: Path):
    # Arrange
    db_path = tmp_path / "db.sqlite"
    repo = SQLitePlaysRepo(db_path)
    p = repo.create_play("Alpha cut", "https://example.com/clip.mp4")
    
    # Act
    ok = repo.delete_play(p.id)
    
    # Assert
    assert ok is True
    
    ok2 = repo.delete_play(p.id)
    assert ok2 is False
    

def test_sqlite_repo_is_thread_safe_for_create_and_list(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    db_path = tmp_path / "db.sqlite"
    repo = SQLitePlaysRepo(db_path)

    def create_n(n, offset):
        for i in range(n):
            repo.create_play(f"T {offset+i}", "https://e.com/a.mp4")

    N_THREADS, N_PER = 5, 10
    with ThreadPoolExecutor(max_workers=N_THREADS) as ex:
        for t in range(N_THREADS):
            ex.submit(create_n, N_PER, t * N_PER)

    items, _ = repo.list_plays(limit=1000)
    assert len(items) == N_THREADS * N_PER
