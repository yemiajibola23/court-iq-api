from fastapi import Request
from pathlib import Path
import os
from app.repositories.plays_repo import PlaysRepository
from app.repositories.sqlite import SQLitePlaysRepo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "db" / "app.sqlite"

def get_repo(request: Request) -> PlaysRepository:
    repo = getattr(request.app.state, "repo", None)
    if repo is None:
        db_path = Path(os.getenv("DB_PATH", str(DEFAULT_DB_PATH)))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        request.app.state.repo = SQLitePlaysRepo(db_path)
        repo = request.app.state.repo
    return repo
