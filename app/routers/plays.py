from fastapi import APIRouter, Response, status, HTTPException, Query
import uuid
from typing import Optional, List

from app.schemas.play import PlayCreateRequest, PlayCreateResponse, PlayRead
from app.repositories import plays_repo

# TECH_DEBT: TD2, TD7  — validate path param `id` as UUID; add negative tests for malformed UUID.
# TECH_DEBT: TD6       — harmonize response field names (playId vs id) across create/read DTOs.

router = APIRouter(prefix="/v1/plays", tags=["plays"])

@router.post("", response_model=PlayCreateResponse, status_code=status.HTTP_201_CREATED)
def create_play(payload: PlayCreateRequest, response: Response) -> PlayCreateResponse:
    play = plays_repo.create(title=payload.title, video_path=payload.video_path)

    response.headers["Location"] = f'/v1/plays/{play.id}'
    return PlayCreateResponse(playId=uuid.UUID(play.id))

@router.get("/{id}")
def get_play(id: str):
    play = plays_repo.get(id)
    if not play:
        raise HTTPException(status_code=404, detail="Play not found")
    
    return PlayRead(id=play.id, title=play.title, video_path=play.video_path)

@router.get("")
def list_plays(limit: int = Query(10, ge=1, le=100), cursor: Optional[str] = None, title: Optional [str] = None):
    try:
        items, next_cursor = plays_repo.list_plays(cursor=cursor, limit=limit, title_prefix=title)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cursor")
    
    dtos: List[PlayRead] = [PlayRead(id=p.id, title=p.title, video_path=p.video_path) for p in items]
    
    return {"data": dtos, "nextCursor": next_cursor}