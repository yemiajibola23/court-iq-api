# 🛠 TECH_DEBT

This file tracks known technical debt and when we plan to address it (aligned to the roadmap).  
**Legend:** Pending ▫️ | In-Progress 🔧 | Resolved ✅

| ID   | Description                                                                                                                                            | When to Address | Status    |
|------|--------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|-----------|
| TD1  | In-memory plays repo instead of persistent storage (SQLite first)                                                                                      | Day 11          | Pending   |
| TD2  | GET `/v1/plays/{id}` lacks strict UUID validation                                                                                                      | Day 9           | Resolved ✅   |
| TD3  | No direct unit tests for `plays_repo` (currently covered only via API tests)                                                                           | Day 10          | Pending   |
| TD4  | `video_path` validation gaps: **https only**, **max length 2048**, allowed extensions `{.mp4,.mov,.m4v,.webm}`                                         | Day 11          | Pending   |
| TD5  | Dev-override flags: `ALLOW_LOCAL_VIDEO_PATHS` / `MEDIA_ROOT` (allow `file://` + relative under `MEDIA_ROOT` only when flag is true)                    | Day 12          | Pending   |
| TD6  | API field naming inconsistency: `PlayCreateResponse.playId` (camel) vs `PlayRead.id` (snake)                                                            | Day 13          | Pending   |
| TD7  | Missing negative tests for malformed UUID on GET `/v1/plays/{id}`                                                                                      | Day 14          | Pending   |
| TD8  | In-memory data store not reset between tests could cause cross-test pollution                                                                          | Day 8           | ✅ Resolved (autouse reset + `clear_store`) |
| TD9  | 422 error format should be **per-field arrays** (e.g., `{ "video_path": ["…"] }`) for all validation failures                                           | Day 11          | Pending   |
| TD10 | Dev-override security: prevent path traversal outside `MEDIA_ROOT` (e.g., `../`)                                                                       | Day 12          | Pending   |
| TD11 | Dev-override UX: precise 422 message like `["local file paths are not allowed in this environment"]` when flag is off                                  | Day 12          | Pending   |
| TD12 | Normalization rules: don’t mutate URL casing except case-insensitive extension checks                                                                  | Day 11          | Pending   |
| TD13 | Introduce `PlayRepository` interface + FastAPI dependency override so tests can use a fresh per-test repo instance                                     | Day 10          | Pending   |
| TD14 | Cursor design: move from plain `id` to composite/opaque token (e.g., `created_at|id`) after DB migration                                               | Day 12          | Pending   |
| TD15 | List polish: add `hasMore` boolean (or compute deterministically) alongside `nextCursor`                                                               | Day 9           | Pending   |
| TD16 | Normalize collection route paths (avoid trailing-slash 405s)                                                                                           | Day 8           | ✅ Resolved |
| TD17 | Centralize Play → DTO mapping to avoid drift                                                                                                           | Day 8           | ✅ Resolved |
| TD18 | Add default‐limit + clamp tests for list (`limit` default 10, clamp to 100)                                                                            | Day 9           | Pending   |
| TD19 | Standardize UUID usage across all endpoints (create, read, delete) for consistency                                                                     | Day 15          | Pending   |
| TD20 | Plan for introducing threading lock or concurrency-safe patterns before DB migration                                                                  | Day 14          | Pending   |
| TD21 | Transactional delete pipeline: cascade deletes (e.g., diagrams, storage blobs, worker jobs)                                         | Day 16                  | Pending   |

---

## Tech Debt Log (grouped details)

### A. Repository & Persistence
- **TD1** – Replace in-memory store with a DB-backed repo (SQLite first).
- **TD13** – Add `PlayRepository` interface and wire routers via dependency injection.
- **TD19** – Standardize UUID usage across all routes to ensure uniform validation and parsing.
- **TD20** – Design concurrency-safe access pattern (threading lock or async lock) for in-memory repo before DB migration.
- **TD21** – Transactional delete pipeline: Once DB and storage layers exist, implement cascading deletes (plays → diagrams, blobs, background jobs).  
  *Why:* Prevents orphaned resources and ensures consistency.  
  *When:* After DB + worker service rollout (Day 16).

### B. Validation & Error Shape
- **TD2 / TD7** – Enforce UUID format for GET by id and add negative tests.
- **TD4 / TD12** – Harden `video_path` validation.
- **TD5 / TD10 / TD11** – Dev-override path rules.
- **TD9** – Standardize 422 error envelope.

### C. Pagination & Filtering
- **TD15** – Add `hasMore` boolean to list responses.
- **TD14** – Switch to composite/opaque cursors post-DB migration.

### D. API Consistency & Mappers
- **TD16** – ✅ Resolved.
- **TD17** – ✅ Resolved.

---
