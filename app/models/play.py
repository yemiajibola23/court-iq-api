from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
@dataclass
class Play:
    id: str
    title: str
    video_path: str
    thumbnail_path: Optional[str] = None
    created_at: datetime = datetime.now(timezone.utc)  # Default to now if not provided