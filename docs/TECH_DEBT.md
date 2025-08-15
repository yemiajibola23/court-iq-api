# 🛠 TECH_DEBT

This file tracks known technical debt and when we plan to address it (aligned to the roadmap).  
**Legend:** Pending ▫️ | In-Progress 🔧 | Resolved ✅

| ID   | Description                                                                                                                                            | When to Address | Status    |
|------|--------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|-----------|
| TD1  | In-memory plays repo instead of persistent storage (SQLite first)                                                                                      | Day 11          | Pending   |
| TD2  | GET `/v1/plays/{id}` lacks strict UUID validation                                                                                                      | Day 9           | Pending   |
| TD3  | No direct unit tests for `plays_repo` (currently covered only via API tests)                                                                            | Day 10          | Pending   |
| TD4  | `video_path` validation gaps: **https only**, **max length 2048**, allowed extensions `{.mp4,.mov,.m4v,.webm}`                                         | Day 11          | Pending   |
| TD5  | Dev-override flags: `ALLOW_LOCAL_VIDEO_PATHS` / `MEDIA_ROOT` (allow `file://` + relative under `MEDIA_ROOT` only when flag is true)                    | Day 12          | Pending   |
| TD6  | API field naming inconsistency: `PlayCreateResponse.playId` (camel) vs `PlayRead.id` (snake)                                                            | Day 13          | Pending   |
| TD7  | Missing negative tests for malformed UUID on GET `/v1/plays/{id}`                                                                                      | Day 14          | Pending   |
| TD8  | In-memory data store not reset between tests could cause cross-test pollution                                                                           | Day 8           | ✅ Resolved (autouse reset + `clear_store`) |
| TD9  | 422 error format should be **per-field arrays** (e.g., `{ "video_path": ["…"] }`) for all validation failures                                           | Day 11          | Pending   |
| TD10 | Dev-override security: prevent path traversal outside `MEDIA_ROOT` (e.g., `../`)                                                                        | Day 12          | Pending   |
| TD11 | Dev-override UX: precise 422 message like `["local file paths are not allowed in this environment"]` when flag is off                                  | Day 12          | Pending   |
| TD12 | Normalization rules: don’t mutate URL casing except case-insensitive extension checks                                                                   | Day 11          | Pending   |
| TD13 | Introduce `PlayRepository` interface + FastAPI dependency override so tests can use a fresh per-test repo instance                                      | Day 10          | Pending   |
| TD14 | Cursor design: move from plain `id` to composite/opaque token (e.g., `created_at|id`) after DB migration                                               | Day 12          | Pending   |
| TD15 | List polish: add `hasMore` boolean (or compute deterministically) alongside `nextCursor`                                                                | Day 9           | Pending   |
| TD16 | Normalize collection route paths (avoid trailing-slash 405s)                                                                                            | Day 8           | ✅ Resolved |
| TD17 | Centralize Play → DTO mapping to avoid drift                                                                                                           | Day 8           | ✅ Resolved |
| TD18 | Add default‐limit + clamp tests for list (`limit` default 10, clamp to 100)                                                                             | Day 9           | Pending   |

---

## Tech Debt Log (grouped details)

### A. Repository & Persistence
- **TD1** – Replace in-memory store with a DB-backed repo (SQLite first). Migrate create/list/show, then backfill tests.
- **TD13** – Add `PlayRepository` interface and wire routers via a `get_repo()` dependency. Tests will use dependency overrides to inject a fresh in-memory repo per test.  
  *Why:* removes module globals, unlocks unit tests for the repo, and isolates state cleanly.

### B. Validation & Error Shape
- **TD2 / TD7** – Enforce UUID format for GET by id and add negative tests.
- **TD4 / TD12** – Harden `video_path` validation (https-only, length ≤ 2048, allowed extensions; case-insensitive ext check only).
- **TD5 / TD10 / TD11** – Dev-override policy for local media: allow `file://` and `MEDIA_ROOT`-relative paths only when flag is on; block traversal; return specific 422 messages.
- **TD9** – Standardize 422 error envelope to per-field arrays via a global exception handler.

### C. Pagination & Filtering
- **TD15** – Add `hasMore` boolean to list responses for ergonomic clients. Keep `nextCursor` as the authoritative continuation token.
- **TD14** – After DB migration, move from plain-id cursors to composite/opaque cursors (e.g., `created_at|id`) to guarantee stable order across shards and future sorts.

### D. API Consistency & Mappers
- **TD16** – ✅ Resolved. Collection routes now use a consistent path (no trailing-slash mismatch causing 405).
- **TD17** – ✅ Resolved. Play → DTO mapping centralized to avoid duplication.

---

## Recently Resolved (Day 8)
- **List endpoint:** Implemented cursor pagination + case-insensitive title-prefix filter (filter-then-paginate).  
- **Bad cursor policy:** Returns `400 {"detail": "Invalid cursor"}` when cursor isn’t in the filtered view.  
- **Test isolation:** Added `clear_store()` and autouse reset fixture to eliminate cross-test leakage.  
- **Routing consistency & mapper refactor:** Normalized collection path; centralized DTO mapping.

---

## Next Up (Days 9–12)
- **Day 9:** Validation polish (UUID check, list default/clamp tests, optional `hasMore`).  
- **Day 10:** Repo DI + unit tests for repo methods.  
- **Day 11:** DB migration (SQLite), `video_path` validator hardening, 422 envelope standardization scaffolding.  
- **Day 12:** Dev-override path policy + traversal protection + precise 422 messages; plan opaque/composite cursors.

