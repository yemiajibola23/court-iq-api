from fastapi import APIRouter, Response, status, HTTPException, Query, Depends, Request
import uuid
from typing import Optional, List, cast
from pathlib import Path

from app.schemas.play import PlayCreateRequestJSON, PlayCreateResponse, PlayRead
from app.utils.mappers import to_play_dto
from app.utils.video_path_policy import ALLOWED_EXTS
from app.deps import get_repo
from app.repositories.plays_repo import PlaysRepository
from fastapi.responses import JSONResponse
from starlette.datastructures import UploadFile as StarletteUploadFile
from app.services.uploads import validate_and_save_upload
from fastapi.responses import JSONResponse

# TECH_DEBT: TD2, TD7  — validate path param `id` as UUID; add negative tests for malformed UUID.
# TECH_DEBT: TD6       — harmonize response field names (playId vs id) across create/read DTOs.

router = APIRouter(prefix="/v1/plays", tags=["plays"])

@router.post("/", response_model=PlayCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_play(response: Response, 
                request: Request,
                plays_repo: PlaysRepository=Depends(get_repo)) -> Response | PlayCreateResponse:
    
    content_type = request.headers.get("content-type", "")
    
    if content_type.lower().startswith("multipart/form-data"):
        form = await request.form()
        upload = cast(Optional[StarletteUploadFile], form.get("file"))
        url = cast(Optional[str], form.get("video_path"))
        title = cast(Optional[str], form.get("title"))
        title_str = (title or "").strip()
        
        if not title_str:
            return JSONResponse(status_code=422, content={"__root__": ["title required"]})

        if url and upload:
            return JSONResponse(status_code=422, content={"__root__": ["provide either file or video_path, not both"]})
        elif not url and not upload:
            return JSONResponse(status_code=422, content={"__root__": ["either file or video_path is required"]})
        else:
            if upload:
                writer = lambda b: None # (no-op)
                result = await validate_and_save_upload(upload, writer=writer, allowed_exts=ALLOWED_EXTS, chunk_size=8192)
                
                match result:
                    case("error", field, msg): 
                        return JSONResponse(status_code=422, content={field: [msg]})
                    case("ok", uri):
                        play = plays_repo.create_play(title=title_str, video_path=uri)
                        response.headers["Location"] = f'/v1/plays/{play.id}'
                        return PlayCreateResponse(playId=uuid.UUID(play.id))
            elif url:
                return JSONResponse(status_code=422, content={"__root__": ["send URLs as JSON"]})
    else:
        data = await request.json()
        obj = PlayCreateRequestJSON.model_validate(data)
        assert obj.video_path is not None # Guaranteed by model-level validator
        
        play = plays_repo.create_play(title=obj.title, video_path=obj.video_path)
        response.headers["Location"] = f'/v1/plays/{play.id}'
        return PlayCreateResponse(playId=uuid.UUID(play.id))

    return JSONResponse(status_code=415, content={"__root__": ["unsupported media type"]})
            
@router.get("/{id}")
def get_play(id: str,
             plays_repo: PlaysRepository=Depends(get_repo)):
    play = plays_repo.get_play(id)
    if not play:
        raise HTTPException(status_code=404, detail="Play not found")
    
    return PlayRead(id=play.id, title=play.title, video_path=play.video_path)

@router.get("/")
def list_plays(
    limit: Optional[int] = Query(None),
    cursor: Optional[str] = None, 
    title: Optional[str] = None,
    plays_repo: PlaysRepository=Depends(get_repo)
):
    
    if limit is None:
        limit = 10
    elif limit < 1:
        limit = 1
    elif limit > 100:
        limit = 100
        
    try:
        items, next_cursor = plays_repo.list_plays(cursor=cursor, limit=limit, title_prefix=title)
    except ValueError:
        return JSONResponse(status_code=422, content={"cursor": ["invalid cursor token"]})
    
    dtos: List[PlayRead] = [to_play_dto(p) for p in items]
    hasMore = next_cursor is not None
    
    return {"data": dtos, "nextCursor": next_cursor, "hasMore": hasMore}

@router.delete("/{id}")
def delete_play(id: str,
                plays_repo: PlaysRepository=Depends(get_repo)):
    key = str(id)
    ok = plays_repo.delete_play(key)
    if not ok:
        raise HTTPException(status_code=404, detail="Play not found")
    
    return Response(status_code=204)