# Day 11 — End of Day Summary

**Focus:** Storage Provider Wiring

## What shipped
- (none)

## Carry-overs
- ✨ feat(storage): add provider interface (local, gcs) (D11-1)
- 🧹 chore(env): add `STORAGE_PROVIDER`, bucket config, emulator flag (D11-2)
- ✅ test(storage): fake provider for unit tests (D11-3)
- 🔨 refactor(services): inject storage provider via service layer (D11-4)
- 📝 docs: storage configuration matrix (D11-5)
- 💳 techdebt(storage): In-memory plays repo instead of persistent storage (SQLite first) (TD1)
- 💳 techdebt: Normalization rules: don’t mutate URL casing except case-insensitive extension checks (TD12)
- 💳 techdebt: `video_path` validation gaps: **http(s) only**, **max length 2048**, allowed extensions `{.mp4,.mov,.m4v,.webm}` (TD4)
- 💳 techdebt: 422 error format should be **per-field arrays** (e.g., `{ "video_path": ["…"] }`) for all validation failures (TD9)

## Tech debt status (today’s IDs)
### Resolved
- (none)
### Still outstanding
- TD1 — In-memory plays repo instead of persistent storage (SQLite first)
- TD4 — `video_path` validation gaps: **http(s) only**, **max length 2048**, allowed extensions `{.mp4,.mov,.m4v,.webm}`
- TD9 — 422 error format should be **per-field arrays** (e.g., `{ "video_path": ["…"] }`) for all validation failures
- TD12 — Normalization rules: don’t mutate URL casing except case-insensitive extension checks

## Tomorrow: suggested first micro-task
- ✨ feat(storage): add provider interface (local, gcs) (D11-1)

> Tip: start with `make day-start DAY=12` then tackle the first carry-over using TDD.
