from __future__ import annotations
from pydantic import BaseModel, field_validator, StringConstraints
from typing import Annotated
from uuid import UUID
from urllib.parse import urlparse, urlsplit
from pathlib import Path
import re
import app.core.config as cfg
from app.utils.video_path_policy import validate_video_path as enforce_path_policy
# TECH_DEBT: TD4, TD9, TD12  — tighten video_path rules (https only, len≤2048, ext in set), per-field 422 arrays, case-insensitive ext check without mutating URL casing.
# TECH_DEBT: TD11            — when flags disallow local paths, return specific 422 message per spec.

# Acceptable non-URL path shapes
RE_UNIX_ABS = re.compile(r"^/[^*?\"<>|]+")
RE_WIN_ABS  = re.compile(r"^[A-Za-z]:\\[^*?\"<>|]+")
RE_REL      = re.compile(r"^\.(\.)?[/\\][^*?\"<>|]+")
ALLOWED_EXTS = {".mp4", ".mov", ".m4v", ".webm"}

class PlayCreateRequest(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    video_path: str
    
    @field_validator("title")
    @classmethod
    def normalize_title(cls, v: str) -> str:
        # Collapse multiple spaces to a single space and strip ends
        v = re.sub(r"\s+", " ", v).strip()
        if not v:
            raise ValueError("title must not be empty")
       
        return v
    
    @field_validator("video_path", mode="before")
    @classmethod
    def validate_video_path(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("video_path must be a string")
        
        kind, _ = enforce_path_policy(v, allow_local=cfg.ALLOW_LOCAL_VIDEO_PATHS, media_root=cfg.MEDIA_ROOT)

        return v
class PlayCreateResponse(BaseModel):
    playId: UUID   
            
class PlayRead(BaseModel):
    id: str
    title: str
    video_path: str