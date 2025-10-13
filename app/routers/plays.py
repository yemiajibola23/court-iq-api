from fastapi import APIRouter, Response, status, HTTPException, Query, Depends, Request
from uuid import UUID
from typing import Optional, List, cast
from pathlib import Path

from app.schemas.play import PlayCreateRequestJSON, PlayCreateResponse, PlayRead, PlaySummary
from app.utils.mappers import to_play_dto
from app.utils.video_path_policy import ALLOWED_EXTS
from app.deps import get_repo, get_storage_client
from app.repositories.plays_repo import PlaysRepository
from fastapi.responses import JSONResponse
from starlette.datastructures import UploadFile as StarletteUploadFile
from app.services.uploads import validate_and_save_upload
from fastapi.responses import JSONResponse
from app.utils.cursor import decode_cursor, encode_cursor
from app.presentation.plays import present_play
from datetime import datetime
from app.services.plays_delete_storage import delete_play_and_media

# TECH_DEBT: TD2, TD7  — validate path param `id` as UUID; add negative tests for malformed UUID.
# TECH_DEBT: TD6       — harmonize response field names (id vs id) across create/read DTOs.

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
                        return PlayCreateResponse(id=UUID(play.id))
            elif url:
                return JSONResponse(status_code=422, content={"__root__": ["send URLs as JSON"]})
    else:
        data = await request.json()
        obj = PlayCreateRequestJSON.model_validate(data)
        assert obj.video_path is not None # Guaranteed by model-level validator
        
        play = plays_repo.create_play(title=obj.title, video_path=obj.video_path)
        response.headers["Location"] = f'/v1/plays/{play.id}'
        return PlayCreateResponse(id=UUID(play.id))

    return JSONResponse(status_code=415, content={"__root__": ["unsupported media type"]})
            
@router.get("/{id}", response_model=PlayRead)
def get_play(id: str,
             plays_repo: PlaysRepository=Depends(get_repo)):
    play = plays_repo.get_play(id)
    if not play:
        raise HTTPException(status_code=404, detail="Play not found")
    
    presented = present_play(play)
    model = PlayRead.model_validate(presented)
    
    return model

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

    before_dt= None
    before_id = None
        
    if cursor and cursor.strip():
        try:
            before_dt, before_id = decode_cursor(cursor)
        except ValueError:
            return JSONResponse(status_code=422, content={"cursor": ["invalid cursor token"]})
        
    items, has_more = plays_repo.list_plays(limit=limit, title_prefix=title, before_dt=before_dt, before_id=before_id)
    next_cursor: str | None = None
        
    if has_more: 
        last = items[-1]
        next_cursor = encode_cursor(last.created_at, UUID(last.id))
    
    dtos: List[PlaySummary] = [to_play_dto(p) for p in items]    
    return {"data": dtos, "nextCursor": next_cursor, "hasMore": has_more}

@router.delete("/{id}")
def delete_play(id: str,
                plays_repo: PlaysRepository=Depends(get_repo),
                storage = Depends(get_storage_client)):
    try:
        delete_play_and_media(play_id=id, repo=plays_repo, storage=storage)
    except KeyError:
        raise HTTPException(status_code=404, detail="Play not found")
    return Response(status_code=204)