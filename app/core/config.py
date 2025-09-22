import os
from dotenv import load_dotenv
from pathlib import Path

# TECH_DEBT: TD5, TD10, TD11 — wire ALLOW_LOCAL_VIDEO_PATHS + MEDIA_ROOT; secure path resolution (no traversal); precise 422 messages when override is off.

# Load .env if present (no-op in prod where env vars are provided by the platform)
load_dotenv()

def _get_bool(name: str, default: bool=False) -> bool:
    """Parse common truthy/falsey strings from env vars."""
    val = os.getenv(name)
    if val is None:
        return default
    
    return val.strip().lower() in ("1", "true", "yes", "on")


def _get_int(name: str, default: int) -> int:
    """Safely parse an int env var; fall back to default on error."""
    val = os.getenv(name)
    if val is None:
        return default
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

def _get_str(name: str, default: str | None = None) -> str | None:
    """Read a string env; treat empty/whitespace as missing."""
    val = os.getenv(name)
    if val is None:
        return default
    val = val.strip()
    return val if val else default

def _normalize_url(name: str, value: str | None) -> str | None:
    """
    Ensure http(s) absolute URL and remove trailing slash to avoid '//' joins.
    Raise early on bad config so problems are obvious at startup.
    """
    if value is None:
        return None
    v = value.strip().rstrip("/")
    if not (v.startswith("http://") or v.startswith("https://")):
        raise ValueError(f"{name} must be an absolute http(s) URL, got: {value!r}")
    return v

def _normalize_placeholder(value: str) -> str:
    """
    Accepts '/path.png' or absolute URL; otherwise normalizes to '/<value>'.
    Keeps things predictable for clients loading a placeholder asset.
    """
    v = (value or "").strip()
    if v.startswith(("http://", "https://", "/")):
        return v
    return "/" + v.lstrip("/")

# ---- Public settings (import these elsewhere) ----
APP_ENV: str = os.getenv("APP_ENV", "local")
PORT: int = _get_int("PORT", 8000)
STORAGE_BUCKET: str = os.getenv("STORAGE_BUCKET", "")
USE_EMULATORS: bool = _get_bool("USE_EMULATORS", True)
ALLOW_LOCAL_VIDEO_PATHS: bool = _get_bool("ALLOW_LOCAL_VIDEO_PATHS", False)

MEDIA_ROOT: Path = Path(os.getenv("MEDIA_ROOT", "./media")).expanduser().resolve()

ALLOW_LOCAL_PREVIEW: bool = _get_bool("ALLOW_LOCAL_PREVIEW")

PUBLIC_CDN_BASE: str | None = _normalize_url("PUBLIC_CDN_BASE", _get_str("PUBLIC_CDN_BASE"))
LOCAL_STATIC_BASE: str | None = _normalize_url("LOCAL_STATIC_BASE", _get_str("LOCAL_STATIC_BASE"))

DEFAULT_THUMB_PLACEHOLDER = "/static/placeholders/thumb-480x270.png"
THUMB_PLACEHOLDER_URL: str =  _normalize_placeholder(
    _get_str("THUMB_PLACEHOLDER_URL", DEFAULT_THUMB_PLACEHOLDER) or DEFAULT_THUMB_PLACEHOLDER
)

def PREVIEW_URL_BASE() -> str | None:
    """
    Origin used to build `videoUrl`/`thumbnailUrl` on read:
    - In local/dev, when previews are allowed and a local static base exists → use LOCAL_STATIC_BASE
    - Otherwise, if a CDN base is configured → use PUBLIC_CDN_BASE
    - Otherwise → None (client won't get a public URL; e.g., rely on future signed URLs)
    """
    if APP_ENV.lower() in {"local", "dev"} and ALLOW_LOCAL_PREVIEW and LOCAL_STATIC_BASE:
        return LOCAL_STATIC_BASE
    if PUBLIC_CDN_BASE:
        return PUBLIC_CDN_BASE
    return None


# Optional: create MEDIA_ROOT in dev to avoid surprises
if APP_ENV.lower() in {"local", "dev"}:
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# Optional: expose what we export (helps with autocomplete)
__all__ = [
    "APP_ENV", "PORT", "STORAGE_BUCKET", "USE_EMULATORS",
    "ALLOW_LOCAL_VIDEO_PATHS", "MEDIA_ROOT",
    "ALLOW_LOCAL_PREVIEW", "PUBLIC_CDN_BASE", "LOCAL_STATIC_BASE",
    "THUMB_PLACEHOLDER_URL", "PREVIEW_URL_BASE",
]