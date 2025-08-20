# app/deps.py

from functools import lru_cache
from app.repositories.plays_repo import PlaysRepository, _assert_protocol
from app.repositories.memory import MemoryRepository

# singleton factory (cached) to keep state across requests when desired
@lru_cache(maxsize=1)
def _singleton_repo() -> PlaysRepository:
    repo = MemoryRepository()
    _assert_protocol(repo, PlaysRepository)
    return repo

def get_repo() -> PlaysRepository:
    return _singleton_repo()
