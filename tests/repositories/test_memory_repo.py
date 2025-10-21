import pytest
from app.repositories.memory import MemoryRepository
from app.repositories.plays_repo import PlaysRepository, _assert_protocol
from uuid import UUID
from datetime import datetime, timezone

@pytest.fixture
def repo():
    r = MemoryRepository()
    yield r
    r.clear()
    
def _seed(repo: PlaysRepository, n, *, title_fmt="Alpha Cut {i:03d}"):
    # helper to create n plays with zero-padded titles
    ids: list[str] = []
    for i in range(n):
        title = title_fmt.format(i=i)
        p = repo.create_play(title, "https://e.com/p.mp4")
        ids.append(p.id)
    return ids
    
def test_memory_repo_conforms():
    _assert_protocol(MemoryRepository, PlaysRepository)
        
def test_create_and_get(repo):
    p = repo.create_play("Spain PnR", "https://e.com/a.mp4")
    got = repo.get_play(p.id)
    assert got is not None
    assert got.id == p.id
    assert got.title == "Spain PnR"

def test_get_unknown_returns_none(repo):
    assert repo.get_play("does-not-exist") is None

def test_delete_then_delete_again(repo):
    p = repo.create_play("X", "https://e.com/a.mp4")
    assert repo.delete_play(p.id) is True
    assert repo.delete_play(p.id) is False

def test_list_default_limit_10(repo):
    _seed(repo, 13)
    items, next_cursor = repo.list_plays(limit=10, before_dt=None, before_id=None, title_prefix=None)
    assert len(items) == 10
    assert isinstance(next_cursor, str) and next_cursor

def test_list_cursor_paginates(repo):
    # Arrange
    _seed(repo, 12)
    
    # Act & Assert
    items, cur= repo.list_plays(limit=7, before_dt=None, before_id=None, title_prefix=None)
    assert len(items) == 7
    assert isinstance(cur, str) and cur
    
    last = items[-1]
    items2, cur2 = repo.list_plays(before_dt=last.created_at, before_id=UUID(last.id), title_prefix=None)
    assert len(items2) == 5
    assert cur2 is None 

def test_list_title_prefix_filter_is_case_insensitive_and_trimmed(repo):
    # Arrange
    repo.create_play("Alpha", "https://e.com/a.mp4")
    repo.create_play("alpha spain", "https://e.com/b.mp4")
    repo.create_play("Beta", "https://e.com/c.mp4")
    
    # Act
    items, next_cursor = repo.list_plays(limit=10, title_prefix="  AlPh  ")
    
    # Assert
    assert [p.title for p in items] == ["alpha spain", "Alpha"]
    assert next_cursor is None
    

def test_list_handles_nonexistent_cutoff_gracefully(repo):
    # Arrange
    _seed(repo, 3)
    before_dt = datetime(1992, 9, 18, 12, 34, 56, 789000, tzinfo=timezone.utc)
    before_id = UUID("12345678-1234-5678-1234-567812345678")
    
    # Act
    items, next_cursor = repo.list_plays(limit=2, before_dt=before_dt, before_id=before_id)
    
    # Assert
    assert len(items) == 0
    assert next_cursor is None