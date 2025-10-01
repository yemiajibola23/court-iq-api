from app.models.play import Play
from app.utils.mappers import resolver_input_from_play
from app.services.url_resolver import build_public_urls
from typing import Dict
from app.schemas.play import PlayRead

def present_play(p: Play) -> PlayRead:
    minimal = resolver_input_from_play(p)
    video_url, thumb_url = build_public_urls(minimal)
    
    return PlayRead(id=p.id,
                    title=p.title,
                    video_path=p.video_path,
                    videoUrl=video_url,
                    thumbnailUrl=thumb_url)
    