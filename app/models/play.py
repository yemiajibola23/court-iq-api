from dataclasses import dataclass
from datetime import datetime

@dataclass
class Play:
    id: str
    title: str
    video_path: str
    created_at: datetime