from dataclasses import dataclass

@dataclass
class Play:
    id: str
    title: str
    video_path: str
    created_at: str