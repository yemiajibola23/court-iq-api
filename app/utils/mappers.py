from app.schemas.play import PlayRead
from app.models.play import Play

def to_play_dto(p: Play) -> PlayRead:
    return PlayRead(id=p.id, title=p.title, video_path=p.video_path) 