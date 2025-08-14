# POST `/v1/plays` — Request Spec & Validation

## Purpose

Create a Play record by providing a title and a reference to its video source. We enforce strict input validation to keep downstream processing reliable.

---

## Request Model

### Fields

- **title** — `string` (required)

  - **Constraints:** trimmed, length `1..100`
  - **Rationale:** concise, human-readable play name
  - **Example:** `Spain Pick-and-Roll vs Drop`

- **video_path** — `string` (required)
  - **Primary (default):** must be an **`https://` URL**
  - **Length:** ≤ 2048
  - **Allowed extensions:** `.mp4`, `.mov`, `.m4v`, `.webm` (case-insensitive on extension only)
  - **Dev-only override:** if `ALLOW_LOCAL_VIDEO_PATHS=true`, also accept:
    - `file://` absolute paths, **or**
    - relative paths under `MEDIA_ROOT` (e.g., `videos/clip.mp4`)
  - **Disallowed:** `http://` (non-TLS), unsupported extensions
  - **Examples:**
    - ✅ `https://cdn.example.com/plays/spain_pr.mp4`
    - ✅ `file:///Users/yemi/Vids/spain_pr.mp4` _(dev only)_
    - ✅ `videos/spain_pr.mp4` _(dev only, under MEDIA_ROOT)_
    - ❌ `http://example.com/clip.mp4` _(must use https)_
    - ❌ `https://cdn.example.com/clip.avi` _(unsupported)_

---

## Validation Rules

1. **Common sanitization**

   - Trim leading/trailing whitespace for both fields.
   - Do not mutate URL casing except for extension comparison.

2. **`title` rules**

   - Reject empty or whitespace-only.
   - Max length 100.

3. **`video_path` rules (default)**

   - Must parse as a valid URL.
   - Scheme must be `https`.
   - Path must end with one of: `.mp4|.mov|.m4v|.webm`.

4. **Dev override (`ALLOW_LOCAL_VIDEO_PATHS=true`)**
   - Accept `file://` absolute paths that end with an allowed extension.
   - Accept **relative** paths only if they resolve under `MEDIA_ROOT` and end with an allowed extension.
   - Still reject empty/whitespace and unsupported extensions.

---

## Error Responses (422 Unprocessable Entity)

Return a per-field error array. Examples:

```json
{
  "title": ["must be a non-empty string (1..100 chars)"],
  "video_path": ["must be https URL with .mp4|.mov|.m4v|.webm"]
}
```

Dev-override example (when flag is off):

```json
{
  "video_path": ["local file paths are not allowed in this environment"]
}
```

## Environment Flags

- `ALLOW_LOCAL_VIDEO_PATHS` — bool (default: false)
- `MEDIA_ROOT` — string directory path used to resolve relative dev paths

## Test Planning

**Happy path**

- Valid `title`, `https` URL with `.mp4` → `200` (or `201`) with `playId`.

**Failure cases**

- Empty `title` → `422.title`.
- `video_path` with `http://` → `422.video_path`.
- `video_path` with unsupported extension `.avi` → `422.video_path`.
- Dev override off: `file://...` and `videos/clip.mp4` → `422.video_path`.
- Dev override on:  same inputs now valid.

## Validation Checklist (Day 5)
- [ ] Sanitize: trim `title`, `video_path`
- [ ] title: non-empty, ≤ 100 chars
- [ ] video_path (default): valid URL, scheme https, ext in {mp4,mov,m4v,webm}, len ≤ 2048
- [ ] Dev override: allow `file://` and relative under `MEDIA_ROOT` (both with allowed ext)
- [ ] 422 error format: per-field arrays
- [ ] Happy path: 201 Created + Location: `/v1/plays/{id}`