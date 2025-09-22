# Day 12 — End of Day Summary

**Focus:** Local path override policy + traversal protection + cursor plan

## What shipped
- ✨ feat(api): `POST /v1/plays` supports multipart upload OR external URL (D12-1)
- ✅ test(api): multipart upload path; url path; invalid types (D12-2)
- 🪄 perf(storage): stream upload and content-type detection (D12-3)
- 🔨 refactor(services): move upload logic out of router (D12-4)
- 📝 docs: curl/HTTPie examples for uploads (D12-5)
- 💳 techdebt(api): Dev-override flags: ALLOW_LOCAL_VIDEO_PATHS / MEDIA_ROOT (allow file:// + relative under MEDIA_ROOT only when flag is true) (TD5)
- 💳 techdebt(api): Dev-override UX: precise 422 message like ["local file paths are not allowed in this environment"] when flag is off (TD11)
- 💳 techdebt(api): Cursor design: move from plain id to composite/opaque token (e.g., created_at) after DB migration (TD14)
- 💳 techdebt: Dev-override security: prevent path traversal outside `MEDIA_ROOT` (e.g., `../`) (TD10)

## Carry-overs
- (none)

## Tech debt status (today’s IDs)
### Resolved
- (none)
### Still outstanding
- TD5 — Dev-override flags: `ALLOW_LOCAL_VIDEO_PATHS` / `MEDIA_ROOT` (allow `file://` + relative under `MEDIA_ROOT` only when flag is true)
- TD10 — Dev-override security: prevent path traversal outside `MEDIA_ROOT` (e.g., `../`)
- TD11 — Dev-override UX: precise 422 message like `["local file paths are not allowed in this environment"]` when flag is off
- TD14 — Cursor design: move from plain `id` to composite/opaque token (e.g., `created_at`) after DB migration

## Tomorrow: suggested first micro-task
- (clear slate 🎉)

> Tip: start with `make day-start DAY=13` then tackle the first carry-over using TDD.
