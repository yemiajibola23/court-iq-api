from __future__ import annotations
from pydantic import BaseModel, field_validator, StringConstraints
from typing import Annotated
from uuid import UUID
from urllib.parse import urlparse
import re


# Acceptable non-URL path shapes
RE_UNIX_ABS = re.compile(r"^/[^*?\"<>|]+")
RE_WIN_ABS  = re.compile(r"^[A-Za-z]:\\[^*?\"<>|]+")
RE_REL      = re.compile(r"^\.(\.)?[/\\][^*?\"<>|]+")

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
    
    @field_validator("video_path")
    @classmethod
    def validate_video_path(cls, v: str) -> str:
        v = v.strip()
        
        # 1. Accept http(s) URLs
        parsed = urlparse(v)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            return v

        # 2) Accept file-like paths (Unix abs, Windows abs, or relative)
        if RE_UNIX_ABS.match(v) or RE_WIN_ABS.match(v) or RE_REL.match(v):
            return v
        
        raise ValueError("video_path must be a http(s) URL or a valid file path")

class PlayCreateResponse(BaseModel):
    playId: UUID   
            
class PlayRead(BaseModel):
    id: str
    title: str
    video_path: str