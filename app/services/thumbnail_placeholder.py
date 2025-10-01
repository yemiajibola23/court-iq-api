from typing import Optional
def build_placeholder(play, mode: str | None, static_url: str | None) -> Optional[str]:
    """
    Return a placeholder thumbnail URL or None based on settings.
    Lean: just 'off' and 'static' for now.
    """
    m = (mode or "off").lower()
    if m == "static":
        return static_url or None
    return None        