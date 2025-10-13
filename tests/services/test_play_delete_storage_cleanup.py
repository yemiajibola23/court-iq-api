import pytest
from uuid import UUID, uuid4
from app.repositories.memory import MemoryRepository
from app.services.plays_delete_storage import delete_play_and_media
from app.core.interfaces import StorageClient
from app.core.logging import LOGGER_NAME, get_logger

class FakeStorage(StorageClient):
    def __init__(self, fail_for=None) -> None:
        self.calls = []
        self.fail_for = set(fail_for or [])
    
    def delete_blob(self, path: str):
        self.calls.append(path)
        if path in self.fail_for:
            raise RuntimeError(f"Simulated delete failure for {path}")
@pytest.fixture
def fake_storage():
    return FakeStorage()

@pytest.fixture
def repo_mem():
    return MemoryRepository()

@pytest.mark.parametrize("use_path", [True, False])
def test_deletes_video_and_thumbnail_blobs_best_effort(fake_storage, media_root, repo_mem, make_play_from_media, use_path):
    # Arrange
    root_dir = media_root()
    
    _, video_fields = make_play_from_media(root_dir, "videos/abc.mp4", use_path=use_path)
    _, thumb_fields = make_play_from_media(root_dir, "thumbnails/abc.jpg", use_path=use_path)
    
    video_blob=video_fields["storage_path"] if use_path else video_fields["storage_key"]
    thumb_blob=thumb_fields["storage_path"] if use_path else thumb_fields["storage_key"]
    
    play = repo_mem.create_play("Delete Me", video_path=video_blob, thumbnail_path=thumb_blob)
    play_id = play.id
    
    # Act
    delete_play_and_media(play_id=play_id, repo=repo_mem, storage=fake_storage)
    
    # Assert
    assert set(fake_storage.calls) == {video_blob, thumb_blob}

def test_unknown_ids_raises_not_found_and_makes_no_storage_calls(fake_storage, repo_mem):
    missing_id = str(uuid4())
    
    with    pytest.raises(ValueError, match="not found"):
        delete_play_and_media(play_id=missing_id, repo=repo_mem, storage=fake_storage)
        
    assert fake_storage.calls == []
    
def test_storage_error_is_logged_but_does_not_fail_delete(fake_storage, media_root, repo_mem, make_play_from_media, caplog):
    # Arrange
    root_dir = media_root()
    
    _, video_fields = make_play_from_media(root_dir, "videos/def.mp4", use_path=True)
    _, thumb_fields = make_play_from_media(root_dir, "thumbnails/def.jpg", use_path=True)
    
    video_blob=video_fields["storage_path"]
    thumb_blob=thumb_fields["storage_path"]
    
    play = repo_mem.create_play("Delete Me", video_path=video_blob, thumbnail_path=thumb_blob)
    play_id = play.id
    
    app_logger = get_logger()
    app_logger.addHandler(caplog.handler)
    
    fake_storage.fail_for.add(video_blob)
    
    # Act
    try:
        with caplog.at_level("WARNING", logger=LOGGER_NAME):
            delete_play_and_media(play_id=play_id, repo=repo_mem, storage=fake_storage)
    finally:
        app_logger.removeHandler(caplog.handler)
    
    assert set(fake_storage.calls) == {video_blob, thumb_blob}
    
    warnings = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warnings) >= 1
    assert "Simulated delete failure" in warnings[0].getMessage()  
    
def test_skips_missing_thumbnail_field(fake_storage, media_root, repo_mem, make_play_from_media):
    root = media_root()
    _, video_fields = make_play_from_media(root, "videos/solo.mp4", use_path=True)
    video_blob = video_fields["storage_path"]

    play = repo_mem.create_play(title="Video Only", video_path=video_blob, thumbnail_path=None)

    from app.services.plays_delete_storage import delete_play_and_media
    delete_play_and_media(play_id=play.id, repo=repo_mem, storage=fake_storage)

    assert fake_storage.calls == [video_blob]

@pytest.mark.parametrize("thumb_value", [None, ""])
def test_skips_none_or_empty_blob_fields(fake_storage, media_root, repo_mem, make_play_from_media, thumb_value):
    # Arrange
    root = media_root()
    _, video_fields = make_play_from_media(root, "videos/solo.mp4", use_path=True)
    video_blob = video_fields["storage_path"]

    play = repo_mem.create_play(title="Video Only", video_path=video_blob, thumbnail_path=thumb_value)

    # Act
    delete_play_and_media(play_id=play.id, repo=repo_mem, storage=fake_storage)
    
    # Assert
    assert fake_storage.calls == [video_blob]