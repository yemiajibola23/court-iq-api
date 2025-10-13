import pytest
from uuid import UUID
from app.repositories.memory import MemoryRepository
from app.services.plays_delete_storage import delete_play_and_media
from app.core.interfaces import StorageClient

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

@pytest.mark.parametrize("use_path", [True])
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

# def test_unknown_ids_raises_not_found_and_makes_no_storage_calls():

# def test_storage_error_is_logged_but_does_not_fail_delete():
    
# def test_skips_none_or_empty_blob_fields():