import pytest
from app.repositories.memory import MemoryRepository
from app.repositories.plays_repo import PlaysRepository, _assert_protocol

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
    items, cur = repo.list_plays(cursor=None, limit=10, title_prefix=None)
    assert len(items) == 10
    assert cur == items[-1].id

def test_list_cursor_paginates(repo):
    _seed(repo, 12)
    p1, c1 = repo.list_plays(limit=7, cursor=None, title_prefix=None)
    p2, c2 = repo.list_plays(limit=7, cursor=c1, title_prefix=None)
    assert len(p1) == 7
    assert len(p2) == 5
    assert c2 is None
    assert set(x.id for x in p1).isdisjoint(set(x.id for x in p2))

def test_list_title_prefix_filter_is_case_insensitive_and_trimmed(repo):
    repo.create_play("Alpha", "https://e.com/a.mp4")
    repo.create_play("alpha spain", "https://e.com/b.mp4")
    repo.create_play("Beta", "https://e.com/c.mp4")
    items, cur = repo.list_plays(limit=10, cursor=None, title_prefix="  AlPh  ")
    assert [p.title for p in items] == ["Alpha", "alpha spain"]
    assert cur is None

def test_list_raises_value_error_for_invalid_cursor(repo):
    _seed(repo, 3)
    with pytest.raises(ValueError):
        repo.list_plays(limit=2, cursor="not-in-store", title_prefix=None)