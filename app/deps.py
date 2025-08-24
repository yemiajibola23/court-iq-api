# app/deps.py

from app.repositories.plays_repo import PlaysRepository
from fastapi import Request


def get_repo(request: Request) -> PlaysRepository:
    return request.app.state.repo
