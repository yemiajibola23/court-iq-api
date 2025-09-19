import pytest
from datetime import datetime, timezone, timedelta
from uuid import UUID
from app.utils.cursor import encode_cursor, decode_cursor
import json, base64

def _b64url_no_pad(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

def test_cursor_round_trip_ok():
    # Arrange
    created_at = datetime(2025, 9, 18, 12, 34, 56, 789000, tzinfo=timezone.utc)
    id_ = UUID("12345678-1234-5678-1234-567812345678")
    
    # Act
    tok = encode_cursor(created_at, id_)
    dt2, id2 = decode_cursor(tok)
    
    # Assert
    assert dt2 == created_at
    assert id2 == id_
    
@pytest.mark.parametrize(
    "token", 
    [
        "not-a-real-token",   # plain junk
        "",                   # empty string
        "$$$",                # invalid chars
        "////",               # still invalid after padding
        "😀",                 # non-ASCII emoji
        "eyJpIjoiYmFkIn0",    # base64url-looking but invalid JSON/payload
    ],
    ids=["junk", "empty", "dollar", "slashes", "emoji", "bad-json-ish"],
)
def test_decode_rejects_garbage_token(token):
    with pytest.raises(ValueError) as execinfo:
        decode_cursor(token)
    assert str(execinfo.value) == "invalid cursor token" 

@pytest.mark.parametrize(
     "payload",
    [
        {"c": "2025-09-18T12:00:00.000Z"},                       # missing "i"
        {"i": str(UUID("12345678-1234-5678-1234-567812345678"))} # missing "c"
    ],
    ids=["missing-i", "missing-c"],
)
def test_decode_rejects_missing_keys(payload):
    token = _b64url_no_pad(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    with pytest.raises(ValueError) as execinfo:
        decode_cursor(token)
    assert str(execinfo.value) == "invalid cursor token" 

def test_encode_rejects_naive_datetime():
    naive_dt = datetime(2025, 9, 18, 12, 0, 0)
    some_id = UUID("12345678-1234-5678-1234-567812345678")
    
    with pytest.raises(ValueError, match=r"^created_at must be timezone-aware in UTC$") as execinfo:
        encode_cursor(naive_dt, some_id)

def test_encode_rejects_non_utc_datetime():
    non_utc = timezone(timedelta(hours=1))
    dt = datetime(2025, 9, 18, 12, 0, 0, tzinfo=non_utc)
    some_id = UUID("12345678-1234-5678-1234-567812345678")
    
    with pytest.raises(ValueError, match=r"^created_at must be timezone-aware in UTC$"):
        encode_cursor(dt, some_id)

@pytest.mark.parametrize(
    "payload",
    [
        {"c": "2025-09-18T12:00:00.000Z", "i": "not-a-uuid"},                          # bad uuid
        {"c": "not-a-date", "i": "12345678-1234-5678-1234-567812345678"},             # bad datetime
    ],
    ids=["bad-uuid", "bad-datetime"],
)
def test_decode_rejects_invalid_payloads(payload):
    token = _b64url_no_pad(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    with pytest.raises(ValueError, match=r"^invalid cursor token$"):
        decode_cursor(token)
        
def test_decode_accepts_base64url_without_padding():
    created_at = datetime(2025, 9, 18, 12, 34, 56, 789000, tzinfo=timezone.utc)
    id_ = UUID("12345678-1234-5678-1234-567812345678")
    
    # Act
    token = encode_cursor(created_at, id_)
    assert "=" not in token
    dt2, id2 = decode_cursor(token)
    
    # Assert
    assert id2 == id_
    assert dt2 == created_at