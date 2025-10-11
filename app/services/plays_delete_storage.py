from uuid import UUID
from app.repositories.plays_repo import PlaysRepository
from app.core.interfaces import StorageClient
from app.core.logging import get_logger
logger = get_logger()

def delete_play_and_media(play_id: str, repo: PlaysRepository, storage: StorageClient) -> None:
    """
    Deletes the play record and attempts to delete associated media files
    (video and thumbnail) from storage. Logs errors but does not fail if
    storage deletion fails.

    Args:
        play_id (str): The ID of the play to delete.
    """
    play = repo.get_play(play_id)
    if not play:
        raise ValueError(f"Play with id {play_id} not found")
    
    repo.delete_play(play_id)
    
    blobs = [play.video_path, play.thumbnail_path]
    seen = set()
    unique_blobs = [b for b in blobs if b and b not in seen and not seen.add(b)]
    
    for blob in unique_blobs:
        try:
            storage.delete_blob(blob)            
            logger.info("event=storage_delete ok=true play_id=%s blob=%s", play_id, blob)
            
        except Exception as e:
            # Log the error; in real code, use logging framework
            logger.warning(f"Error deleting blob {blob}: {e}")   