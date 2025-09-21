from typing import Protocol, Optional, Tuple, List, runtime_checkable
from app.models.play import Play
from datetime import datetime
from uuid import UUID

def _assert_protocol(obj: object, proto: type) -> None:
    """
    Assert that an object or class conforms to a Protocol at runtime.

    Args:
        obj: The object or class to check.
        proto: The Protocol to enforce.
    Raises:
        AssertionError: If obj does not implement the Protocol.
    """
    if not isinstance(obj, proto):
        raise AssertionError(
            f"{obj.__class__.__name__} does not conform to {proto.__name__}"
        )

@runtime_checkable
class PlaysRepository(Protocol):
    # create and return a play
    def create_play(self, title: str, video_path: str) -> Play: ...
    
    # get a play by id or None
    def get_play(self, id: str) -> Optional[Play]: ...

    # list plays with optional cursor, limit, and title prefix filter
    def list_plays(self, *, limit: int = 10, title_prefix: Optional[str] = None, before_dt: Optional[datetime]=None, before_id:Optional[UUID]=None) -> Tuple[List[Play], Optional[str]]: ...
    
    # delete by id, true if something was deleted
    def delete_play(self, id: str) -> bool: ...
    
    # test convenience; clear in-memory state
    def clear(self) -> None: ...
