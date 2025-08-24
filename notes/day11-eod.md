# Day 11 — End of Day Summary

**Focus:** SQLite migration + validator + 422

## What shipped
- ✨ feat(db): add SQLite schema + connection bootstrap (D11-1)
- ✨ feat(repos): `SQLitePlaysRepo` (`create_play`, `get_play`, `list_plays`, `delete_play`, `clear`) (D11-2)
- 🔨 refactor(api): default repo → SQLite via dependency; keep test override (D11-3)
- ✅ test(repos/api): CRUD + prefix filter + cursor pagination (D11-4)
- ✨ feat(validation): harden `video_path` (http(s), ≤2048, {.mp4,.mov,.m4v,.webm}) (D11-5)

## Carry-overs
- ✨ feat(api): global 422 handler with per-field arrays (D11-6)
- 📝 docs: README error examples; update TECH_DEBT resolved items (TD1, TD12; TD4/TD9 once implemented) (D11-7)

## Tech debt status (today’s IDs)
### Resolved
- (none)
### Still outstanding
- TD1 — In-memory plays repo instead of persistent storage (SQLite first)
- TD4 — `video_path` validation gaps: **http(s) only**, **max length 2048**, allowed extensions `{.mp4,.mov,.m4v,.webm}`
- TD9 — 422 error format should be **per-field arrays** (e.g., `{ "video_path": ["…"] }`) for all validation failures
- TD12 — Normalization rules: don’t mutate URL casing except case-insensitive extension checks

## Tomorrow: suggested first micro-task
- ✨ feat(api): global 422 handler with per-field arrays (D11-6)

> Tip: start with `make day-start DAY=12` then tackle the first carry-over using TDD.
