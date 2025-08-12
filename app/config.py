import os
from dotenv import load_dotenv

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

# ---- Public settings (import these elsewhere) ----
APP_ENV: str = os.getenv("APP_ENV", "local")
PORT: int = _get_int("PORT", 8000)
STORAGE_BUCKET: str = os.getenv("STORAGE_BUCKET", "")
USE_EMULATORS: bool = _get_bool("USE_EMULATORS", True)

# Optional: expose what we export (helps with autocomplete)
__all__ = ["APP_ENV", "PORT", "STORAGE_BUCKET", "USE_EMULATORS"]