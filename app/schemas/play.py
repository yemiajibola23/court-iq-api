from __future__ import annotations
from pydantic import BaseModel, field_validator, StringConstraints, Field, ConfigDict
from typing import Annotated, Optional
from uuid import UUID
import re
import app.core.config as cfg
from app.utils.video_path_policy import validate_video_path as enforce_path_policy

# Acceptable non-URL path shapes
RE_UNIX_ABS = re.compile(r"^/[^*?\"<>|]+")
RE_WIN_ABS  = re.compile(r"^[A-Za-z]:\\[^*?\"<>|]+")
RE_REL      = re.compile(r"^\.(\.)?[/\\][^*?\"<>|]+")
ALLOWED_EXTS = {".mp4", ".mov", ".m4v", ".webm"}
class PlayCreateRequestJSON(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    video_path: str
    
    @field_validator("video_path", mode="before")
    @classmethod
    def validate_video_path(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("video_path must be a string")
        else:
            enforce_path_policy(v, allow_local=cfg.ALLOW_LOCAL_VIDEO_PATHS, media_root=cfg.MEDIA_ROOT)

        return v
    
    @field_validator("title")
    @classmethod
    def normalize_title(cls, v: str) -> str:
        # Collapse multiple spaces to a single space and strip ends
        v = re.sub(r"\s+", " ", v).strip()
        if not v:
            raise ValueError("title must not be empty")
       
        return v
class PlayCreateResponse(BaseModel):
    playId: UUID   
            
class PlayRead(BaseModel):
    id: str
    title: str
    video_path: str
    video_url: Optional[str] = Field(None, alias="videoUrl", serialization_alias="videoUrl")
    thumbnail_url: str = Field(..., alias="thumbnailUrl", serialization_alias="thumbnailUrl")

    model_confg = ConfigDict(populate_by_name=True)