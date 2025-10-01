from app.schemas.play import  PlaySummary
from app.models.play import Play
from dataclasses import is_dataclass, asdict
from typing import Any, Optional, Dict, List, cast

def to_play_dto(p: Play) -> PlaySummary:
    return PlaySummary(id=p.id, title=p.title, video_path=p.video_path) 

def _first_str(mapping: Dict[str, Any], names: List[str]) -> Optional[str]:
    """Return first non-empty string found in mapping by trying names in order."""
    for n in names:
        v = mapping.get(n)
        if isinstance(v, str) and v.strip():
            return v
    return None


def resolver_input_from_play(play: object) -> dict[str, str]:
    """
    Adapt a Play (dataclass, Pydantic v1/v2, or dict-like) to the minimal resolver input:
      { "storage_path": <str>?, "storage_key": <str>? }
    Only includes keys that exist and are non-empty strings.
    """
    
    play_dict: Dict[str, Any] = {}
    if is_dataclass(play) and not isinstance(play, type):
        play_dict = asdict(play)
    else:
        md = getattr(play, "model_dump", None)
        if callable(md):
            res = md()
            play_dict = cast(Dict[str, Any], res) if isinstance(res, dict) else {}
        else:
            d = getattr(play, "dict", None)
            if callable(d):
                res = d()
                play_dict = cast(Dict[str, Any], res) if isinstance(res, dict) else {}
            elif isinstance(play, dict):
                play_dict = play
            else:
                play_dict = {
                    "storage_path": getattr(play, "storage_path", None),
                    "storage_key": getattr(play, "storage_key", None),
                    "video_path": getattr(play, "video_path", None),
                    "videoPath": getattr(play, "videoPath", None),
                    "storagePath": getattr(play, "storagePath", None),
                    "storageKey": getattr(play, "storageKey", None),
                }

    out: dict[str, str] = {}
    path = _first_str(play_dict, ["storage_path", "storagePath", "storage_key", "storageKey"])
    if path is not None:
        out["storage_path"] = path
    
    key = _first_str(play_dict, ["storage_key", "storageKey"])
    if key is not None:
        out["storage_key"] = key
    
        
    return out
    