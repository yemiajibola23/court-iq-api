from fastapi import APIRouter
from uuid import uuid4

from app.schemas.play import PlayCreateRequest, PlayCreateResponse

router = APIRouter(prefix="/v1/plays", tags=["plays"])

# Temporary in-memory store for Day 6 (will be replaced with repo on Day 7+)
_PLAYS = {}

@router.post("", response_model=PlayCreateResponse)
def create_play(payload: PlayCreateRequest) -> PlayCreateResponse:
    play_id = uuid4()
    _PLAYS[str(play_id)] = {
        "id": str(play_id),
        "title": payload.title,
        "video_path": payload.video_path,
    }
    
    return PlayCreateResponse(playId=play_id)
