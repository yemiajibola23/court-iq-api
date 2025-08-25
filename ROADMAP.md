# CourtIQ – 40-Day Hybrid Roadmap (Checklist Only)

_Each item is a suggested commit. Keep using the branch naming convention per day._

## Day 1 – Backend Repo Setup

- [x] ✨ feat: Create Python virtual environment and install dependencies (D1-1)
- [x] 📝 docs: Add `README.md` with initial project description (D1-2)
- [x] 📝 docs: Add `COLLAB_GUIDELINES.md` with Hybrid CourtIQ Dev Flow description (D1-3)
- [x] ✨ feat: Create `app/main.py` with placeholder `/health` route (D1-4)
- [x] ✅ test: Write test for `/health` endpoint (D1-5)
- [x] Final commit for Day 1 (D1-6)
- [x] Push branch `feat/backend-setup` (D1-7)

## Day 2 – Commit Conventions and Workflow Docs

- [x] 📝 docs: Document commit message format in `CONTRIBUTING.md` (D2-1)
- [x] 📝 docs: Document branch naming conventions in `CONTRIBUTING.md` (D2-2)
- [x] 📝 docs: Add `WORKFLOW.md` with high-level dev process (D2-3)
- [x] 📝 docs: Include notes on when to commit & push (D2-4)
- [x] Final commit for Day 2 (D2-5)
- [x] Push branch `docs/workflow-and-commit-style` (D2-6)

## Day 3 – Project Folder & Config Structure

- [x] ✨ feat: Add `app/` with `routes`, `models`, `services` folders (D3-1)
- [x] 🧹 chore: Add `tests/` folder for pytest (D3-2)
- [x] ✨ feat: Create `.env.example` for environment variables (D3-3)
- [x] ✨ feat: Add `config.py` for loading env vars at runtime (D3-4)
- [x] Final commit for Day 3 (D3-5)
- [x] Push branch `chore/folder-and-config-setup` (D3-6)

## Day 4 – Env Loading & Health Check

- [x] ✨ feat: Update `config.py` to load `.env` at runtime with type-safe helpers (D4-1)
- [x] 🧹 chore: Install `python-dotenv` (D4-2)
- [x] 🧹 chore: Install `uvicorn` and run project locally (D4-3)
- [x] ✅ test: Verify `/health` endpoint responds correctly (D4-4)
- [x] Final commit for Day 4 (D4-5)
- [x] Push branch `chore/env-loading-and-health` (D4-6)

## Day 5 – `/plays` Endpoint Validation Plan

- [x] 📝 docs: Define request model fields (title, video_path) in notes (D5-1)
- [x] 📝 docs: Define validation rules (non-empty strings, valid video path format) (D5-2)
- [x] ✅ test: Create placeholder test for `/v1/plays` happy path and validation (D5-3)
- [x] Final commit for Day 5 (D5-4)
- [x] Push branch `test/plays-endpoint-scaffolding` (D5-5)

## Day 6 – Create Play (POST)

- [x] ✨ feat(api): add `POST /v1/plays` with Pydantic validation (title, video_path) (D6-1)
- [x] ✅ test(api): happy path returns 200 with `playId` (D6-2)
- [x] ✅ test(api): validation errors (missing/empty fields) return 422 (D6-3)
- [x] 🧹 chore: wire router import in `main.py` (D6-4)
- [x] 📝 docs: update API section in README with request/response (D6-5)

## Day 7 – Get Play (GET by id)

- [x] ✨ feat(api): add `GET /v1/plays/{id}` returning play DTO (D7-1)
- [x] ✅ test(api): returns 404 for unknown id (D7-2)
- [x] 🔨 refactor(models): introduce Play domain model + schema mapping (D7-3)
- [x] 🧹 chore: seed in-memory repo for tests (D7-4)
- [x] 📝 docs: document endpoint and errors (D7-5)

## Day 8 – List Plays (GET with pagination/filter)

- [x] ✨ feat(api): add `GET /v1/plays?cursor=&limit=&title=` pagination + filter (D8-1)
- [x] ✅ test(api): pagination (limit/cursor) and filtering by title prefix (D8-2)
- [x] 🔨 refactor(repos): list method with stable sort + cursor (D8-3)
- [x] 🧹 chore: add test fixtures for multiple plays (D8-4)
- [x] 📝 docs: list endpoint usage examples (D8-5)

## Day 9 – Delete Play

- [x] ✨ feat(api): add `DELETE /v1/plays/{id}` → 204 (D9-1)
- [x] ✅ test(api): 204 on success, 404 on unknown id (D9-2)
- [ ] 🔨 refactor(repos): transactional delete pipeline (future cascade hooks) (D9-3)
- [x] 🧹 chore: tighten router error handling (D9-4)
- [x] 📝 docs: deletion side-effects note (future storage cleanup) (D9-5)

## Day 10 – Validation polish + list clamps

- [x] ✨ feat(api): harden `video_path` validation (https-only; length ≤ 2048; extensions {.mp4,.mov,.m4v,.webm}) (D10-1)
- [x] ✅ test(api): list default limit = 10; clamp to [1,100] (D10-2)
- [x] 🔨 refactor(api): optional `hasMore` boolean in list response (D10-3)
- [x] 📝 docs: update README examples and error shapes (D10-4)

## Day 11 – SQLite migration + validator + 422

**Objective:** SQLite migration + video_path validator hardening + 422 envelope

- [x] ✨ feat(db): add SQLite schema + connection bootstrap (D11-1)
- [x] ✨ feat(repos): `SQLitePlaysRepo` (`create_play`, `get_play`, `list_plays`, `delete_play`, `clear`) (D11-2)
- [x] 🔨 refactor(api): default repo → SQLite via dependency; keep test override (D11-3)
- [x] ✅ test(repos/api): CRUD + prefix filter + cursor pagination (D11-4)
- [x] ✨ feat(validation): harden `video_path` (http(s), ≤2048, {.mp4,.mov,.m4v,.webm}) (D11-5)
- [x] ✨ feat(api): global 422 handler with per-field arrays (D11-6)
- [x] 📝 docs: README error examples; update TECH_DEBT resolved items (TD1, TD12; TD4/TD9 once implemented) (D11-7)

## Day 12 – Local path override policy + traversal protection + cursor plan

**Objective:** Local path override policy + traversal protection + cursor plan

- [ ] ✨ feat(api): `POST /v1/plays` supports multipart upload OR external URL (D12-1)
- [ ] ✅ test(api): multipart upload path; url path; invalid types (D12-2)
- [ ] 🪄 perf(storage): stream upload and content-type detection (D12-3)
- [ ] 🔨 refactor(services): move upload logic out of router (D12-4)
- [ ] 📝 docs: curl/HTTPie examples for uploads (D12-5)
- [ ] 💳 techdebt(api): Dev-override flags: ALLOW_LOCAL_VIDEO_PATHS / MEDIA_ROOT (allow file:// + relative under MEDIA_ROOT only when flag is true) (TD5)
- [ ] 💳 techdebt(api): Dev-override UX: precise 422 message like ["local file paths are not allowed in this environment"] when flag is off (TD11)
- [ ] 💳 techdebt(api): Cursor design: move from plain id to composite/opaque token (e.g., created_at) after DB migration (TD14)

- [ ] 💳 techdebt: Dev-override security: prevent path traversal outside `MEDIA_ROOT` (e.g., `../`) (TD10)

## Day 13 – Public/Preview Video URLs

- [ ] ✨ feat(storage): generate public/preview URL field on play read (D13-1)
- [ ] ✅ test(storage): url shape and fallback when restricted (D13-2)
- [ ] 🔨 refactor(schemas): add `videoUrl` and `thumbnailUrl` (D13-3)
- [ ] 🧹 chore: thumbnail placeholder generator hook (D13-4)
- [ ] 📝 docs: client usage & caching hints (D13-5)
- [ ] 💳 techdebt(api): API field naming inconsistency: `PlayCreateResponse.playId` (camel) vs `PlayRead.id` (snake)

## Day 14 – Delete Video with Play

- [ ] ✨ feat(storage): remove blobs when play deleted (D14-1)
- [ ] ✅ test(api): delete play removes storage object (D14-2)
- [ ] 🔨 refactor(repos): transactional delete pipeline (best-effort) (D14-3)
- [ ] 🧹 chore(logging): structured logs for storage ops (D14-4)
- [ ] 📝 docs: failure scenarios & retries (not guaranteed) (D14-5)
- [ ] 💳 techdebt(routers): Missing negative tests for malformed UUID on GET /v1/plays/{id} (TD7)
- [ ] 💳 techdebt(db) Plan for introducing threading lock or concurrency-safe patterns before DB migration (TD20)

## Day 15 – Signed URLs (Secure Access)

- [ ] ✨ feat(storage): add signed URL generation (time-limited) (D15-1)
- [ ] ✅ test(storage): expiry honored; invalid keys rejected (D15-2)
- [ ] ✨ feat(api): `GET /v1/plays/{id}/video:signed` (D15-3)
- [ ] 🧹 chore(env): key/cred env validation (D15-4)
- [ ] 📝 docs: security trade-offs and TTL defaults (D15-5)
- [ ] 💳 techdebt(api): Standardize UUID usage across all endpoints (create, read, delete) for consistency (TD19)

## Day 16 – Worker Service Skeleton

- [ ] ✨ feat(workers): add processing worker package (separate module) (D16-1)
- [ ] 🧹 chore(queue): define job schema for `process_video` (D16-2)
- [ ] ✅ test(workers): enqueue/dequeue with in-memory queue (D16-3)
- [ ] 🔨 refactor(app): emit job after successful upload (D16-4)
- [ ] 📝 docs: local dev loop for worker (D16-5)
- [ ] techdebt(workers) Transactional delete pipeline: cascade deletes (e.g., diagrams, storage blobs, worker jobs) (TD21)

## Day 17 – Frame Extraction

- [ ] ✨ feat(process): extract frames at N fps using OpenCV (D17-1)
- [ ] ✅ test(process): sample video → expected number of frames (D17-2)
- [ ] 🪄 perf(process): skip duplicate/near-identical frames (D17-3)
- [ ] 🧹 chore(media): temp scratch dir handling & cleanup (D17-4)
- [ ] 📝 docs: fps config & trade-offs (D17-5)

## Day 18 – Detection (Players & Ball)

- [ ] ✨ feat(ml): integrate YOLO model wrapper (players, ball) (D18-1)
- [ ] ✅ test(ml): detection smoke tests on sample frames (D18-2)
- [ ] 🪄 perf(ml): batch inference (D18-3)
- [ ] 🧹 chore(models): label map & confidence thresholds in config (D18-4)
- [ ] 📝 docs: model source, versioning, and reproducibility (D18-5)

## Day 19 – Diagram JSON Generation

- [ ] ✨ feat(process): convert deteions → normalized diagram JSON (D19-1)
- [ ] ✅ test(process): geometry & timeline consistency checks (D19-2)
- [ ] 🔨 refactor(schemas): define `Diagram` schema + validation (D19-3)
- [ ] 🧹 chore: add sanitizers for outliers/missing frames (D19-4)
- [ ] 📝 docs: diagram schema contract (D19-5)

## Day 20 – Persist Diagram to Backend

- [ ] ✨ feat(api): `POST /v1/plays/{id}/diagram` (internal worker call) (D20-1)
- [ ] ✅ test(api): e2e—from video upload to stored diagram (D20-2)
- [ ] 🔨 refactor(repos): diagram store & retrieval abstraction (D20-3)
- [ ] 🧹 chore(security): internal auth or shared secret for worker (D20-4)
- [ ] 📝 docs: diagram lifecycle (D20-5)

## Day 21 – Serve Diagram (GET)

- [ ] ✨ feat(api): `GET /v1/plays/{id}/diagram` returns latest diagram (D21-1)
- [ ] ✅ test(api): 404 when missing; happy path for existing (D21-2)
- [ ] 🧹 chore(http): ETag/Last-Modified caching headers (D21-3)
- [ ] 🪄 perf(repos): projection-only read for large diagrams (D21-4)
- [ ] 📝 docs: client caching guidance (D21-5)

## Day 22 – Manual Diagram Edits (POST)

- [ ] ✨ feat(api): `POST /v1/plays/{id}/diagram:edit` accepts deltas (D22-1)
- [ ] ✅ test(api): schema-validated deltas; rejects invalid ops (D22-2)
- [ ] 🔨 refactor(services): merge engine for deltas (D22-3)
- [ ] 🧹 chore(audit): store editor + timestamp metadata (D22-4)
- [ ] 📝 docs: edit operations and invariants (D22-5)

## Day 23 – Diagram Validation Rules

- [ ] ✨ feat(schemas): strict validation rules (bounds, team sizes, frames) (D23-1)
- [ ] ✅ test(validation): boundary and edge cases (D23-2)
- [ ] 🔨 refactor(process): pre-validate worker output (D23-3)
- [ ] 🧹 chore: error taxonomy (user vs system) (D23-4)
- [ ] 📝 docs: validation spec (D23-5)

## Day 24 – Diagram Diffing & History

- [ ] ✨ feat(api): `GET /v1/plays/{id}/diagram:diff?from=&to=` (D24-1)
- [ ] ✅ test(api): diffs across versions; empty diff case (D24-2)
- [ ] 🔨 refactor(repos): versioned diagram storage (D24-3)
- [ ] 🧹 chore: migration note for versioning (D24-4)
- [ ] 📝 docs: diff format and examples (D24-5)

## Day 25 – E2E Tests (Play → Diagram)

- [ ] ✅ test(e2e): upload video → processed → diagram persisted → read back (D25-1)
- [ ] 🧹 chore(ci): run worker tests in pipeline (D25-2)
- [ ] 🧹 chore: test data fixtures for videos & expected diagrams (D25-3)
- [ ] 🪄 perf: parallelize test jobs (D25-4)
- [ ] 📝 docs: how to run e2e locally (D25-5)

## Day 26 – iOS App Skeleton (SwiftUI)

- [ ] ✨ feat(ios): create CourtIQ SwiftUI app project (D26-1)
- [ ] 🧹 chore(ios): set up bundle ids, targets, schemes (D26-2)
- [ ] ✨ feat(ios): basic app navigation shell (list → detail) (D26-3)
- [ ] 📝 docs(ios): build & run instructions (D26-4)

## Day 27 – iOS Plays List

- [ ] ✨ feat(ios): list view fetching `GET /v1/plays` (D27-1)
- [ ] ✅ test(ios): snapshot UI test for empty + populated lists (D27-2)
- [ ] 🔨 refactor(ios): data layer with async/await + decoding (D27-3)
- [ ] 🧹 chore(ios): environment config (base URL) (D27-4)
- [ ] 📝 docs(ios): API usage sample (D27-5)

## Day 28 – iOS Play Detail + Video

- [ ] ✨ feat(ios): detail screen with title/notes + video player (D28-1)
- [ ] 🔨 refactor(ios): caching for signed video URL (D28-2)
- [ ] ✅ test(ios): detail rendering with mock data (D28-3)
- [ ] 🧹 chore(ios): accessibility labels for key controls (D28-4)
- [ ] 📝 docs(ios): troubleshooting playback (D28-5)

## Day 29 – iOS Diagram Overlay

- [ ] ✨ feat(ios): render diagram overlay synced to video time (D29-1)
- [ ] 🪄 perf(ios): throttle redraw, reuse paths (D29-2)
- [ ] ✅ test(ios): unit tests for frame-to-time mapping (D29-3)
- [ ] 🔨 refactor(ios): diagram view model to parse JSON (D29-4)
- [ ] 📝 docs(ios): overlay architecture notes (D29-5)

## Day 30 – iOS Edit Metadata

- [ ] ✨ feat(ios): edit title/notes (PATCH) with optimistic UI (D30-1)
- [ ] ✅ test(ios): form validation and error states (D30-2)
- [ ] 🔨 refactor(ios): reusable API client + error mapping (D30-3)
- [ ] 🧹 chore(ios): loading/empty/error visuals (D30-4)
- [ ] 📝 docs(ios): UX patterns used (D30-5)

## Day 31 – AI Summary

- [ ] ✨ feat(ai): generate short play summary (rule/LLM hybrid or stub) (D31-1)
- [ ] ✅ test(ai): deterministic tests with fixtures/stubs (D31-2)
- [ ] ✨ feat(api): `GET /v1/plays/{id}/insights/summary` (D31-3)
- [ ] 🔨 refactor(services): insights service abstraction (D31-4)
- [ ] 📝 docs: assumptions & limitations (D31-5)

## Day 32 – Success/Failure Reasoning

- [ ] ✨ feat(ai): simple heuristics using diagram data (spacing, possession) (D32-1)
- [ ] ✅ test(ai): cases for success/failure classification (D32-2)
- [ ] ✨ feat(api): include reasoning in insights payload (D32-3)
- [ ] 🧹 chore: metrics counters for insights calls (D32-4)
- [ ] 📝 docs: feature flags to disable per-env (D32-5)

## Day 33 – Confidence Scores

- [ ] ✨ feat(ai): attach confidence per insight component (D33-1)
- [ ] ✅ test(ai): confidence ranges + aggregation tests (D33-2)
- [ ] 🔨 refactor(schemas): insights schema v1 with confidences (D33-3)
- [ ] 🧹 chore: serialize/rounding standards (D33-4)
- [ ] 📝 docs: interpretation guidance (D33-5)

## Day 34 – Serve Insights API

- [ ] ✨ feat(api): `GET /v1/plays/{id}/insights` (D34-1)
- [ ] ✅ test(api): insights endpoint integration tests (D34-2)
- [ ] 🧹 chore: caching headers & TTL for insights (D34-3)
- [ ] 🔨 refactor(services): batch compute on demand vs cached (D34-4)
- [ ] 📝 docs: endpoint examples (D34-5)

## Day 35 – Dockerize Backend

- [ ] ✨ feat(devops): add Dockerfile + .dockerignore (D35-1)
- [ ] 🧹 chore(devops): multi-stage build for slim image (D35-2)
- [ ] ✅ test(ci): docker build + healthcheck run (D35-3)
- [ ] 🪄 perf(devops): enable uvicorn workers via env (D35-4)
- [ ] 📝 docs: local docker run instructions (D35-5)

## Day 36 – CI/CD Backend

- [ ] ✨ feat(ci): GitHub Actions workflow (lint, test, build image) (D36-1)
- [ ] 🧹 chore(ci): cache deps, parallelize test matrix (D36-2)
- [ ] ✅ test(ci): required checks for PR merge (D36-3)
- [ ] 🧹 chore(ci): tag images by branch/commit (D36-4)
- [ ] 📝 docs: CI overview & secrets management (D36-5)

## Day 37 – Deploy Backend

- [ ] ✨ feat(devops): deploy to Cloud Run (or equivalent) (D37-1)
- [ ] 🧹 chore(devops): infra configs (service, concurrency, min instances) (D37-2)
- [ ] ✅ test(devops): smoke test deployed `/health` (D37-3)
- [ ] 🔨 refactor(config): production env and secrets wiring (D37-4)
- [ ] 📝 docs: rollout & rollback process (D37-5)

## Day 38 – TestFlight Build (iOS)

- [ ] ✨ feat(ios-devops): set up signing, app IDs, profiles (D38-1)
- [ ] 🧹 chore(ios-devops): fastlane lane for beta deploy (optional) (D38-2)
- [ ] ✅ test(ios-devops): archive build succeeds locally (D38-3)
- [ ] 🧹 chore(ios): app metadata + screenshots placeholders (D38-4)
- [ ] 📝 docs(ios-devops): TestFlight checklist (D38-5)

## Day 39 – Documentation Pass

- [ ] 📝 docs: expand README with API table and iOS setup (D39-1)
- [ ] 📝 docs: add `ROADMAP-HYBRID.md` reference and status (D39-2)
- [ ] 📝 docs: add troubleshooting & FAQ (D39-3)
- [ ] 🧹 chore: clean TODOs, rename ambiguous symbols (D39-4)
- [ ] 🧹 chore: tag v0.1.0 and generate changelog (D39-5)

## Day 40 – Bug Fix & Polish Buffer

- [ ] 🚑 fix: address top reported bugs from testing (D40-1)
- [ ] 💄 style: refine UI spacing/typography on iOS (D40-2)
- [ ] 🪄 perf: profile slow endpoints and optimize N+1s (D40-3)
- [ ] 🧹 chore: archive tech-debt items not in scope (D40-4)
- [ ] 📝 docs: “What’s next” and contribution welcome notes (D40-5)

## Meta Improvements & Tooling

### Pre-commit & Validation

- ✅ Integrated `docs-refresh` into pre-commit with stable timestamps (SCRIPTS.md no longer drifts).
- ✅ Added `pre-commit clean + reinstall` troubleshooting step to CONTRIBUTING.
- ✅ Clarified role of `validate_plan.py` and `validate_structure.py` in both pre-commit and CI.

### Documentation & Conventions

- ✅ Expanded CONTRIBUTING.md:
  - Branch naming (`day#-feature`).
  - Commit messages (Conventional Commits + emojis).
  - PR template requiring roadmap objective + tech debt resolution.
- ✅ Added daily flow checklist for contributors (update plan.yml, roadmap, tech debt → validate → commit → PR).
- ✅ Added troubleshooting guide for common validator/pre-commit errors.

### Planning Alignment

- ✅ Reinforced `meta/plan.yml` as the single source of truth (`current_day` must match roadmap).
- ✅ Locked down ROADMAP ↔ TECH_DEBT ↔ Plan sync rules (objectives must match exactly; TD resolved/added must be documented).
- ✅ Documented hybrid dev flow in CONTRIBUTING (validators + pre-commit + CI).
- ✅ Ensured only **today’s day** is validated, future days are flexible.

### Impact

These meta improvements:

- Increase **consistency** across commits, branches, and PRs.
- Enforce **automation** via validators and pre-commit hooks.
- Improve **clarity** for contributors by making expectations explicit.
- Enhance **scalability** by preventing roadmap/tech debt drift as the project grows.
