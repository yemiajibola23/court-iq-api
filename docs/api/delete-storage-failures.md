# DELETE `/v1/plays/{id}` — Delete Play and Cleanup Storage

Deletes a play record and attempts to remove associated blobs (video and thumbnail) from storage.  
Blob cleanup is **best-effort** — storage failures are logged but do not fail the request.

---
 
## Behavior

| Step | Action | Outcome |
|------|---------|----------|
| 1 | Delete record from repository (DB or in-memory) | Always attempted first |
| 2 | For each non-empty blob (`video_path`, `thumbnail_path`) call `storage.delete_blob()` | Each call independent; failures are logged |
| 3 | Respond to client | Always returns `204 No Content` if record deleted; never retries inside the request |

---

## Responses

| Code | Meaning | Notes |
|------|----------|-------|
| **204 No Content** | Play deleted successfully | Blob deletions may still fail silently; see logs |
| **404 Not Found** | No record with that ID | No storage calls are made |
| **422 Unprocessable Entity** | Malformed UUID | No storage calls are made |

**Example**

```bash
curl -i -X DELETE http://localhost:8000/v1/plays/2b9e4f7b-1234-5678-9abc-def012345678
```

**Response**

```
HTTP/1.1 204 No Content
```

---

## Logging

Storage operations are emitted as structured log lines:

| Level | Event | Example |
|--------|--------|----------|
| `INFO` | Successful delete | `event=storage_delete ok=true play_id=2b9e4f7b blob=gs://court-iq/plays/clip.mp4` |
| `WARNING` | Failed delete | `event=storage_delete ok=false play_id=2b9e4f7b blob=gs://court-iq/plays/clip.mp4 error="403 Forbidden"` |

> Failures are *not retried* automatically.  
> Use these logs to identify residual blobs for manual cleanup.

---

## Failure Scenarios

| Scenario | Example cause | API Response | Log | Follow-up |
|-----------|----------------|---------------|-----|------------|
| Record deleted; both blobs removed | — | 204 | 2× ok=true | ✅ All clean |
| Record deleted; video deletion failed | Network/auth error | 204 | 1 ok=false + 1 ok=true | Manual cleanup possible |
| Record deleted; both deletions failed | Storage outage | 204 | 2× ok=false | Manual cleanup required |
| Unknown ID | Record missing | 404 | — | No cleanup attempted |
| Malformed ID | Not a UUID | 422 | — | No cleanup attempted |

---

## Retries (Not Guaranteed)

- No automatic retries are performed during or after the request.  
- Retry scheduling will be introduced in a later milestone.

**Current recommendation**

1. Filter logs for failed deletions:

   ```bash
   grep 'event=storage_delete ok=false' app.log
   ```

2. Re-attempt deletion manually using admin tooling or script:

   ```python
   from app.services.storage import get_storage_client
   storage = get_storage_client()
   storage.delete_blob("gs://court-iq/plays/clip.mp4")
   ```

---

## Design Rationale

- Keeps DELETE requests **fast and idempotent**.  
- Prevents client-visible 5xxs from transient storage issues.  
- Enables future background job to retry failed blobs asynchronously.

---

## Future Improvements (Post-D14)

| Planned Feature | Description |
|-----------------|--------------|
| Background job | Queue failed deletions and retry with backoff |
| Dead-letter handling | Persist unrecoverable failures for operator review |
| Structured JSON logging | Include `trace_id`, `storage_provider`, and `attempt` |
| Metrics | Track success/failure rates of storage deletes |
| Strict mode | Optional flag that fails DELETE when storage is unavailable |
