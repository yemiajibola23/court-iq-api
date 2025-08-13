from fastapi import APIRouter, Response, status
from uuid import uuid4

from app.schemas.play import PlayCreateRequest, PlayCreateResponse

router = APIRouter(prefix="/v1/plays", tags=["plays"])

# Temporary in-memory store for Day 6 (will be replaced with repo on Day 7+)
_PLAYS = {}

@router.post("", response_model=PlayCreateResponse, status_code=status.HTTP_201_CREATED)
def create_play(payload: PlayCreateRequest, response: Response) -> PlayCreateResponse:
    play_id = uuid4()
    _PLAYS[str(play_id)] = {
        "id": str(play_id),
        "title": payload.title,
        "video_path": payload.video_path,
    }
    
    response.headers["Location"] = f'/v1/plays/{play_id}'
    return PlayCreateResponse(playId=play_id)
