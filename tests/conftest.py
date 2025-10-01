import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.memory import MemoryRepository
from typing import Callable, List, Dict, Optional, Tuple, Union, Iterable
import uuid
from app.deps import get_repo
from pathlib import Path
import os, sys
import importlib
import app.services.url_resolver as resolver
from importlib import import_module, reload

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


# Optional: keep sticky values from leaking between tests
@pytest.fixture(autouse=True)
def _neutralize_env(monkeypatch) -> None:
    # Ensure these exist (even as ""), so python-dotenv won't refill them
    for k in ("PUBLIC_CDN_BASE", "LOCAL_STATIC_BASE", "ALLOW_LOCAL_PREVIEW"):
        monkeypatch.setenv(k, "")
    # no yield needed
    
@pytest.fixture
def set_env_and_reload(monkeypatch) -> Callable[..., Tuple[object, object]]:
    """
    Set URL-policy env vars for this test, then reload config and resolver by name.
    Returns (cfg_module, resolver_module).
    """
    def apply(
        *,
        app_env: Optional[str] = None,
        media_root: Optional[Union[str, Path]] = None,
        public_cdn: Optional[str] = None,
        local_static_base: Optional[str] = None,
        allow_local_preview: Optional[str] = None,
        thumbnail_placeholder_mode: Optional[str] = None,
        thumbnail_placeholder: Optional[str] = None) -> Tuple[object, object]:
        # 1) Clear then set env vars for this test
        for key in ("APP_ENV", "MEDIA_ROOT", "PUBLIC_CDN_BASE", "LOCAL_STATIC_BASE", "ALLOW_LOCAL_PREVIEW"):
            monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv("APP_ENV", app_env or "local")

        if media_root is not None:
            mr = str(media_root if isinstance(media_root, Path) else media_root)
            monkeypatch.setenv("MEDIA_ROOT", mr)

        # Empty string blocks python-dotenv from refilling missing vars
        monkeypatch.setenv("PUBLIC_CDN_BASE", public_cdn or "")
        monkeypatch.setenv("LOCAL_STATIC_BASE", local_static_base or "")

        if allow_local_preview is not None:
            monkeypatch.setenv("ALLOW_LOCAL_PREVIEW", str(allow_local_preview))
        else:
            monkeypatch.setenv("ALLOW_LOCAL_PREVIEW", "")
            
        if thumbnail_placeholder_mode is not None:
            monkeypatch.setenv("THUMBNAIL_PLACEHOLDER_MODE", thumbnail_placeholder_mode or "off")
            
        if thumbnail_placeholder is not None:
            monkeypatch.setenv("THUMB_PLACEHOLDER_URL", thumbnail_placeholder or "") 

        # 2) Reload modules by name (ensures identity with sys.modules)
        cfg_mod = import_module("app.core.config")
        reload(cfg_mod)

        resolver_mod = import_module("app.services.url_resolver")
        reload(resolver_mod)

        return cfg_mod, resolver_mod

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
def make_play_from_media() -> Callable[..., tuple[Path, dict[str, str]]]:
    def create(media_root: Path, rel: str = "videos/abc.mp4", *, use_path: bool = True):
        rel_norm = rel.replace("\\", "/")
        abs_path = media_root / rel_norm
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.touch(exist_ok=True)
        if use_path:
            return abs_path, {"storage_path": abs_path.as_posix()}
        else:
            return abs_path, {"storage_key": rel.replace("\\", "/")}
    return create
