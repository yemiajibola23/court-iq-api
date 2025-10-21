# Plays API

This document shows canonical request/response examples for the Plays endpoints, including both **JSON (external URL)** and **multipart (file upload)** flows, and precise **422 validation** formats.

---

## POST `/v1/plays`

Create a new play.

### JSON (external URL)

**Request body**

```json
{
  "title": "Spain PnR vs Drop",
  "video_path": "https://example.com/clip.mp4"
}
```

**Validation**

- `title`: required; trimmed; 1–120 chars.
- `video_path`: required; ≤ 2048 chars; must be an **http(s)** URL with extension **.mp4**, **.mov**, **.m4v**, or **.webm** (case-insensitive).
- Dev override (local paths via JSON):
  - When `ALLOW_LOCAL_VIDEO_PATHS=true`, relative paths under `MEDIA_ROOT` and `file://` URIs are allowed; traversal outside `MEDIA_ROOT` is rejected with `["path must be within MEDIA_ROOT"]`.
  - When the flag is **off**, local paths are rejected with `["local file paths are not allowed in this environment"]`.

**Response**

- **201 Created**
- Headers: `Location: /v1/plays/{id}`
- Body:

```json
{ "id": "2c8e0a09-8a6b-4b3b-8f6d-7d2e2e6f3f71" }
```

**Examples**

_HTTPie_

```bash
http -v POST :8000/v1/plays \
  title="Spain PnR vs Drop" \
  video_path="https://example.com/clip.mp4"
```

_curl_

```bash
curl -i -X POST http://localhost:8000/v1/plays \
  -H "Content-Type: application/json" \
  -d '{"title":"Spain PnR vs Drop","video_path":"https://example.com/clip.mp4"}'
```

---

### Multipart (file upload)

Use multipart when sending a file instead of a URL.

_HTTPie_

```bash
http -v -f POST :8000/v1/plays \
  title="Baseline pick-and-roll" \
  file@clip.mp4 Content-Type:video/mp4
```

_curl_

```bash
curl -i -X POST http://localhost:8000/v1/plays \
  -F 'title=Baseline pick-and-roll' \
  -F 'file=@clip.mp4;type=video/mp4'
```

**Validation**

- `title`: required (same rules as JSON).
- `file`: required **or** `video_path` (but **not both**).
- Allowed extensions: **.mp4**, **.mov**, **.m4v**, **.webm**.
- Magic sniffing:
  - MP4/QuickTime: must contain an `ftyp` box at byte offset 4.
  - WebM: must start with EBML header `\x1A\x45\xDF\xA3`.
- URLs are **not** accepted in multipart: if you send `video_path` in a form, you’ll get `["send URLs as JSON"]`.

**Response**

- **201 Created**
- Headers: `Location: /v1/plays/{id}`
- Body:

```json
{ "id": "2c8e0a09-8a6b-4b3b-8f6d-7d2e2e6f3f71" }
```

---

### 422 Validation

Errors are returned as a map of **field → [messages]**. Non-field messages use `__root__`.

- **Neither file nor URL (JSON without `video_path`, or form without `file`/`video_path`):**

```json
{ "__root__": ["either file or video_path is required"] }
```

- **Both provided (multipart form has `file` and `video_path`):**

```json
{ "__root__": ["provide either file or video_path, not both"] }
```

- **Unsupported extension (multipart):**

```json
{ "file": ["unsupported extension; allowed: .m4v, .mov, .mp4, .webm"] }
```

- **Magic/content mismatch (multipart):**

```json
{ "file": ["file content does not match extension"] }
```

- **Multipart URL sent (instead of JSON):**

```json
{ "__root__": ["send URLs as JSON"] }
```

- **Local path policy (JSON) when flag off:**

```json
{ "video_path": ["local file paths are not allowed in this environment"] }
```

- **Traversal outside `MEDIA_ROOT` (JSON) when flag on:**

```json
{ "video_path": ["path must be within MEDIA_ROOT"] }
```

---

## GET `/v1/plays/{id}`

Returns a Play DTO.

**Response 200**

```json
{
  "id": "b1a6c3f0-9c97-4c8f-8c31-0a6b0a2d6d2e",
  "title": "Spain PnR",
  "video_path": "https://example.com/clip.mp4",
  "video_url": null,
  "thumbnail_url": "/static/placeholders/thumb-480x270.png"
}
```

**Response 404**

```json
{ "detail": "Play not found" }
```

_HTTPie_

```bash
http :8000/v1/plays/b1a6c3f0-9c97-4c8f-8c31-0a6b0a2d6d2e
```

---

## GET `/v1/plays` — List Plays (cursor pagination + title prefix filter)

**Query Params**
| Name | Type | Required | Notes |
|----------|------|----------|-------|
| `limit` | int | no | Default **10**, min 1, max 100. |
| `cursor` | str | no | Opaque cursor token (planned; currently accepts last `id` until migration). |
| `title` | str | no | Case-insensitive, trimmed **prefix** filter. |

**Response**

```json
{
  "data": [{ "id": "f7b3…", "title": "Alpha Cut", "video_path": "https://…" }],
  "nextCursor": "3c9e…",
  "hasMore": true
}
```

**Examples**

_First Page_

```bash
curl -s 'http://localhost:8000/v1/plays?limit=2'
```

_Next Page_

```bash
curl -s 'http://localhost:8000/v1/plays?limit=2&cursor=<cursor-from-previous-response>'
```

_Filter by title prefix_

```bash
curl -s 'http://localhost:8000/v1/plays?limit=10&title=  alpha  '
```

_Invalid cursor (current behavior may return 400/422 depending on migration state)_

```bash
curl -i 'http://localhost:8000/v1/plays?cursor=bogus'
```

> Note: We’re moving from plain-id cursors to an opaque token (created_at + id). The examples above remain valid; behavior is forward-compatible.

---

## DELETE `/v1/plays/{id}` — Delete Play by ID

Deletes the Play record and attempts to remove associated media from storage (video + thumbnail).  
Blob cleanup is **best-effort** — deletion errors are logged but do not cause the request to fail.

**Response codes**

| Code | Meaning | Notes |
|------|----------|-------|
| **204 No Content** | Play deleted successfully | Storage cleanup best-effort |
| **404 Not Found** | No Play with that id | No cleanup attempted |
| **422 Unprocessable Entity** | Invalid UUID | No cleanup attempted |

**Example**

```bash
curl -i -X DELETE http://localhost:8000/v1/plays/2b9e4f7b-1234-5678-9abc-def012345678
```

**Response**
```
HTTP/1.1 204 No Content
```

**See Also**
[Detailed Failure Scenarios & Retry Policy](/docs/api/delete-storage-failures.md)

---

## Environment flags (local path policy)

- `ALLOW_LOCAL_VIDEO_PATHS` — when `true`, JSON `video_path` may be a relative path under `MEDIA_ROOT` or a `file://` URI. When `false`, local paths are rejected.
- `MEDIA_ROOT` — directory that anchors relative paths when the flag is enabled. Traversal outside this directory is rejected.
