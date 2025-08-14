# 🛠 TECH_DEBT

This file tracks known technical debt items and when we plan to address them (aligned to the roadmap).

| ID  | Description                                                                                                                                              | When to Address                         | Status   |
|-----|----------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|----------|
| TD1 | In‑memory plays repo instead of persistent storage                                                                                                       | Day 8 – replace with DB‑backed repo      | Pending  |
| TD2 | GET `/v1/plays/{id}` does not validate that `id` is a proper UUID                                                                                       | Day 9 – add UUID validation              | Pending  |
| TD3 | No direct unit tests for `plays_repo` functions (only covered via API tests)                                                                             | Day 10 – add repo unit tests             | Pending  |
| TD4 | Schema gaps: `video_path` must enforce **https only**, **max length 2048**, and **allowed extensions** `{.mp4,.mov,.m4v,.webm}`                          | Day 11 – extend Pydantic validators      | Pending  |
| TD5 | Dev‑override flags: respect `ALLOW_LOCAL_VIDEO_PATHS` and `MEDIA_ROOT`; allow `file://` and **relative under MEDIA_ROOT** only when flag is true         | Day 12 – enforce config flag logic       | Pending  |
| TD6 | API response naming inconsistency: `PlayCreateResponse.playId` (camel) vs `PlayRead.id` (snake)                                                          | Day 13 – unify API response fields       | Pending  |
| TD7 | No negative tests for malformed UUID on GET `/v1/plays/{id}`                                                                                             | Day 14 – add malformed ID tests          | Pending  |
| TD8 | In‑memory data store not reset between tests could cause cross‑test pollution                                                                             | Day 15 – add store reset between tests   | Pending  |
| TD9 | 422 error format should be **per‑field arrays** (e.g., `{ "video_path": ["…"] }`) for all validation failures                                             | Day 11 – standardize error shape         | Pending  |
| TD10| Dev‑override security: ensure **no path traversal** outside `MEDIA_ROOT` for relative inputs (e.g., `../` segments)                                       | Day 12 – secure path resolution          | Pending  |
| TD11| Dev‑override UX: return specific 422 like `["local file paths are not allowed in this environment"]` when flag is off                                    | Day 12 – precise error messaging         | Pending  |
| TD12| Validation casing rules: do not mutate URL casing except for **extension comparison** (case‑insensitive ext check)                                       | Day 11 – finalize normalization rules    | Pending  |


# Tech Debt Log

This document tracks known technical debt and when it will be addressed, aligned with the [CourtIQ Roadmap](ROADMAP.md).

---

## Outstanding Items

### 1. **Validation: Dev Override for Local Video Paths**
**Description:**  
Implement `ALLOW_LOCAL_VIDEO_PATHS` and `MEDIA_ROOT` logic for POST `/v1/plays`:
- Accept `file://` absolute paths (allowed extensions only).
- Accept relative paths under `MEDIA_ROOT`.
- Still reject when override is off.
- Return correct 422 error format when disallowed.

**Reason for Deferral:**  
Feature flagged for dev use only; can be implemented after main happy path and validation are stable.

**Target Resolution:**  
**Day 8** — while expanding `/v1/plays` logic for pagination and filtering.

---

### 2. **Backfill: 422 Error Format Consistency**
**Description:**  
Ensure all field validation errors follow the agreed per-field array format:
```json
{
  "title": ["error message"],
  "video_path": ["error message"]
}
```
This applies to all endpoints, not just POST /v1/plays.

**Reason for Deferral:**  
Can be standardized once multiple endpoints exist so we can apply a global exception handler.

**Target Resolution:**  
Day 9 — during DELETE /v1/plays implementation and router error handling refactor.

### 3. **In-Memory Repo → Persistent Store**
**Description**
Replace the in-memory repository (used for GET/POST /v1/plays) with a persistent database (likely SQLite first).

**Reason for Deferral**
Replace the in-memory repository (used for GET/POST /v1/plays) with a persistent database (likely SQLite first).

**Target Resolution**
**Day 11** — when wiring up the storage provider and adjusting service layer.

### 4. **Schema Mapping Refactor**
**Description**
Ensure mapping between domain model (Play) and API DTOs is centralized to prevent duplication and drift.

**Reason for Deferral**
Currently lightweight enough to maintain inline; centralizing will make more sense once more endpoints consume Play data.

**Target Resolution**
**Day 10** — when adding PATCH /v1/plays/{id} with partial updates.

### 5. **Test Coverage Gaps**
**Description**
Backfill skipped tests for POST /v1/plays edge cases:
- .avi unsupported extension.
- Local file path rejection/acceptance (with/without override).
- Relative path handling under MEDIA_ROOT.

**Reason for Deferral**
Will require dev override logic from Item #1.

**Target Resolution**
**Day 8** — when dev override logic is implemented.