from datetime import datetime, timedelta
from uuid import UUID
import json, base64
import binascii

def _b64url_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

def _b64url_decode(s: str) -> bytes:
    pad_len = (-len(s)) % 4
    s += "=" * pad_len
    return base64.urlsafe_b64decode(s)

def encode_cursor(created_at: datetime, id_: UUID) -> str:
    if created_at.tzinfo is None or created_at.tzinfo.utcoffset(created_at) != timedelta(0):
        raise ValueError("created_at must be timezone-aware in UTC")
    payload = { "c": created_at.isoformat(timespec="milliseconds").replace("+00:00", "Z"), "i": str(id_) } 
    
    data = json.dumps(payload, separators=(",", ":"),sort_keys=True).encode("utf-8")
    
    return _b64url_encode(data)

def decode_cursor(token: str) -> tuple[datetime, UUID]:
    try:
        data = _b64url_decode(token)
        obj = json.loads(data)
        c: str = obj.get("c"); i = obj.get("i")
        if not c or not i:
            raise ValueError

        if c.endswith("Z"):
            c = c.replace("Z", "+00:00")
            
        c_dt = datetime.fromisoformat(c)
    
        if c_dt.tzinfo is None or c_dt.tzinfo.utcoffset(c_dt) != timedelta(0):
            raise ValueError
        
        uuid_obj = UUID(i)
    except (ValueError, json.JSONDecodeError, binascii.Error, TypeError):
        raise  ValueError("invalid cursor token")
    
    return (c_dt, uuid_obj)
        