import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.memory import MemoryRepository
from typing import Callable, List, Dict, Optional
import uuid
from app.deps import get_repo
from pathlib import Path
import os, sys
import importlib
import app.core.config as cfg
import app.services.url_resolver as resolver

@pytest.fixture(scope="function")
def client():
    # One repo instance for the whole test (persists across requests within the test)
    repo = MemoryRepository()
    repo.clear()

    app.dependency_overrides[get_repo] = lambda: repo
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def assert_201_field():
    def _assert(res):
        assert res.status_code == 201
        data = res.json()
        assert "playId" in data
        
        # Validate UUID-ish value (FastAPI serializes UUID -> string)
        uuid_val = data["playId"]
        uuid.UUID(uuid_val)
    
        assert "Location" in res.headers
        # Location header
        location = res.headers["Location"]
        assert location.startswith("/v1/plays/")

        # The id in Location should equal the JSON playId
        loc_id = location.rsplit("/", 1)[-1]
        assert loc_id == uuid_val
        
    return _assert

@pytest.fixture(scope="function")
def assert_422_field():
    def _assert(res, field: str, contains: str | None=None):
        assert res.status_code == 422
        data = res.json()
        
        # per-field arrays like {"video_path": ["…", "…"], "title": ["…"]}
        assert isinstance(data, dict), data
        assert field in data, f"{field} not in {data}"
        assert isinstance(data[field], list) and all(isinstance(m, str) for m in data[field])
        # optional: at least one non-empty message
        assert any(m.strip() for m in data[field])
        
        if contains is not None:
            assert any(contains in m for m in data[field]) , data[field]
    
    return _assert


@pytest.fixture(scope="function")
def seed_many_plays(client) -> Callable[[List[Dict]], List[Dict]]:
    """
    Returns a function that accepts a list of play stubs and seeds them via POST /v1/plays.
    Each stub should at least include {'title': '...'}.
    Returns the list of created Play DTOs (in the same order).
    """
    def _seed(stubs: List[Dict]) -> List[Dict]:
        created: List[Dict] = []
        for i, stub in enumerate(stubs, start=1):
            # Minimal valid payload 
            payload = {
                "title": stub["title"],
                "video_path": stub.get("video_path", f"https://example.com/clip{i}.mp4")
            }
            
            # POST to create
            res = client.post("/v1/plays", json=payload)
            assert res.status_code == 201, res.text
             
            location = res.headers.get("Location")
            assert location and location.startswith("/v1/plays/"), f"Missing Location header: {res.headers}"

            # fetch the created resource to get a DTO with 'id'
            show = client.get(location)
            assert show.status_code == 200, show.text
            created.append(show.json())
            
        return created
    
    return _seed
class FakeUpload:
        def __init__(self, data:bytes, filename: str="clip.mp4"):
            self._data = data
            self.filename = filename
            self._pos = 0
            
        async def read(self, n: int) -> bytes:
            chunk = self._data[self._pos:self._pos+n]
            self._pos += len(chunk)
            
            return chunk
            
        async def seek(self, pos: int):
            self._pos = pos

@pytest.fixture
def fake_upload_factory():
    def _make(data: bytes, filename: str = "clip.mp4") -> FakeUpload:
        return FakeUpload(data, filename)
    return _make

@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def set_env_and_reload(monkeypatch):
    """
    Factory: set URL-policy env vars and reload cfg/resolver hermetically.
    Usage:
      set_env_and_reload(app_env="local",
                         media_root=str(tmp_path/"media"),
                         public_cdn="https://cdn.local",
                         local_static_base=None,
                         allow_local_preview="false")
    """
    def apply(*, app_env=None, media_root=None, public_cdn=None, local_static_base=None, allow_local_preview=None):
        if public_cdn is None:
            monkeypatch.setenv("PUBLIC_CDN_BASE", "")
        if local_static_base is None:
            monkeypatch.setenv("LOCAL_STATIC_BASE", "")
        if allow_local_preview is None:
            # ensure falsey regardless of .env
            monkeypatch.setenv("ALLOW_LOCAL_PREVIEW", "false")
        
        # Set environment overrides       
        if app_env is not None:
            monkeypatch.setenv("APP_ENV", str(app_env))
        if media_root is not None:
            mr = str(media_root) if isinstance(media_root, (Path,)) else str(media_root)
            monkeypatch.setenv("MEDIA_ROOT", mr)
        if public_cdn is not None:
            monkeypatch.setenv("PUBLIC_CDN_BASE", str(public_cdn))
        if local_static_base is not None:
            monkeypatch.setenv("LOCAL_STATIC_BASE", str(local_static_base))
        if allow_local_preview is not None:
            monkeypatch.setenv("ALLOW_LOCAL_PREVIEW", str(allow_local_preview ))
    
        importlib.reload(cfg)
        importlib.reload(resolver)

        return cfg, resolver
    
    
    return apply

@pytest.fixture
def media_root(tmp_path, set_env_and_reload) -> Callable[..., Path]:
    """
    Create a temporary MEDIA_ROOT, bind env policy, reload cfg/resolver, and return the Path.
    Usage:
        media = media_root(
            app_env="local",
            allow_local_preview="true",
            local_static_base="http://localhost:8000/static",
            public_cdn=None,          # or "https://cdn.local" if testing CDN
            root_name="media"         # optional subdir under tmp_path
        )
    """
    def create(
        *,
        app_env: str = "local",
        allow_local_preview: Optional[str] = None,
        local_static_base: Optional[str] = None,
        public_cdn: Optional[str] = None,
        root_name: str = "media",
    ) -> Path:
        root = tmp_path / root_name
        root.mkdir(parents=True, exist_ok=True)

        # Bind env + reload so resolver sees this MEDIA_ROOT and policy
        set_env_and_reload(
            app_env=app_env,
            media_root=str(root),
            allow_local_preview=allow_local_preview,
            local_static_base=local_static_base,
            public_cdn=public_cdn,
        )
        return root

    return create

@pytest.fixture
def make_play_from_media():
    def create(media_root: Path, rel: str = "videos/abc.mp4", *, use_path: bool = True):
        abs_path = media_root / rel
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.touch(exist_ok=True)
        if use_path:
            return abs_path, {"storage_path": abs_path.as_posix()}
        else:
            return abs_path, {"storage_key": rel.replace("\\", "/")}
    return create
