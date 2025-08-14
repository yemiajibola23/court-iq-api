from fastapi import APIRouter, Response, status, HTTPException
import uuid

from app.schemas.play import PlayCreateRequest, PlayCreateResponse, PlayRead
from app.repositories import plays_repo

router = APIRouter(prefix="/v1/plays", tags=["plays"])

# Temporary in-memory store for Day 6 (will be replaced with repo on Day 7+)


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