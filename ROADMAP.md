# CourtIQ – 40-Day Hybrid Roadmap (Checklist Only)
_Each item is a suggested commit. Keep using the branch naming convention per day._

## Day 1 – Backend Repo Setup

- [x] ✨ feat: Create Python virtual environment and install dependencies
- [x] 📝 docs: Add `README.md` with initial project description
- [x] 📝 docs: Add `COLLAB_GUIDELINES.md` with Hybrid CourtIQ Dev Flow description
- [x] ✨ feat: Create `app/main.py` with placeholder `/health` route
- [x] ✅ test: Write test for `/health` endpoint
- [x] Final commit for Day 1
- [x] Push branch `feat/backend-setup`

## Day 2 – Commit Conventions and Workflow Docs

- [x] 📝 docs: Document commit message format in `CONTRIBUTING.md`
- [x] 📝 docs: Document branch naming conventions in `CONTRIBUTING.md`
- [x] 📝 docs: Add `WORKFLOW.md` with high-level dev process
- [x] 📝 docs: Include notes on when to commit & push
- [x] Final commit for Day 2
- [x] Push branch `docs/workflow-and-commit-style`

## Day 3 – Project Folder & Config Structure

- [x] ✨ feat: Add `app/` with `routes`, `models`, `services` folders
- [x] 🧹 chore: Add `tests/` folder for pytest
- [x] ✨ feat: Create `.env.example` for environment variables
- [x] ✨ feat: Add `config.py` for loading env vars at runtime
- [x] Final commit for Day 3
- [x] Push branch `chore/folder-and-config-setup`

## Day 4 – Env Loading & Health Check

- [x] ✨ feat: Update `config.py` to load `.env` at runtime with type-safe helpers
- [x] 🧹 chore: Install `python-dotenv`
- [x] 🧹 chore: Install `uvicorn` and run project locally
- [x] ✅ test: Verify `/health` endpoint responds correctly
- [x] Final commit for Day 4
- [x] Push branch `chore/env-loading-and-health`

## Day 5 – `/plays` Endpoint Validation Plan

- [x] 📝 docs: Define request model fields (title, video_path) in notes
- [x] 📝 docs: Define validation rules (non-empty strings, valid video path format)
- [x] ✅ test: Create placeholder test for `/v1/plays` happy path and validation
- [x] Final commit for Day 5
- [x] Push branch `test/plays-endpoint-scaffolding`

## Day 6 – Create Play (POST)

- [x] ✨ feat(api): add `POST /v1/plays` with Pydantic validation (title, video_path)
- [x] ✅ test(api): happy path returns 200 with `playId`
- [x] ✅ test(api): validation errors (missing/empty fields) return 422
- [x] 🧹 chore: wire router import in `main.py`
- [x] 📝 docs: update API section in README with request/response

## Day 7 – Get Play (GET by id)

- [x] ✨ feat(api): add `GET /v1/plays/{id}` returning play DTO
- [x] ✅ test(api): returns 404 for unknown id
- [x] 🔨 refactor(models): introduce Play domain model + schema mapping
- [x] 🧹 chore: seed in-memory repo for tests
- [x] 📝 docs: document endpoint and errors

## Day 8 – List Plays (GET with pagination/filter)
**Objective:** GET /v1/plays with pagination & title filter

- [x] ✨ feat(api): add `GET /v1/plays?cursor=&limit=&title=` pagination + filter
- [x] ✅ test(api): pagination (limit/cursor) and filtering by title prefix
- [x] 🔨 refactor(repos): list method with stable sort + cursor
- [X] 🧹 chore: add test fixtures for multiple plays
- [x] 📝 docs: list endpoint usage examples

## Day 9 – Delete Play
**Objective:** Delete Play

- [x] ✨ feat(api): add `DELETE /v1/plays/{id}` → 204
- [x] ✅ test(api): 204 on success, 404 on unknown id
- [ ] 🔨 refactor(repos): transactional delete pipeline (future cascade hooks)
- [x] 🧹 chore: tighten router error handling
- [x] 📝 docs: deletion side-effects note (future storage cleanup)

## Day 10 – Validation polish + list clamps
**Objective:** Validation polish + list clamps

- [x] ✨ feat(api): harden `video_path` validation (https-only; length ≤ 2048; extensions {.mp4,.mov,.m4v,.webm})
- [x] ✅ test(api): list default limit = 10; clamp to [1,100]
- [x] 🔨 refactor(api): optional `hasMore` boolean in list response
- [x] 📝 docs: update README examples and error shapes

## Day 11 – Storage Provider Wiring

- [ ] ✨ feat(storage): add provider interface (local, gcs)
- [ ] 🧹 chore(env): add `STORAGE_PROVIDER`, bucket config, emulator flag
- [ ] ✅ test(storage): fake provider for unit tests
- [ ] 🔨 refactor(services): inject storage provider via service layer
- [ ] 📝 docs: storage configuration matrix

## Day 12 – Video Upload on Create

- [ ] ✨ feat(api): `POST /v1/plays` supports multipart upload OR external URL
- [ ] ✅ test(api): multipart upload path; url path; invalid types
- [ ] 🪄 perf(storage): stream upload and content-type detection
- [ ] 🔨 refactor(services): move upload logic out of router
- [ ] 📝 docs: curl/HTTPie examples for uploads

## Day 13 – Public/Preview Video URLs

- [ ] ✨ feat(storage): generate public/preview URL field on play read
- [ ] ✅ test(storage): url shape and fallback when restricted
- [ ] 🔨 refactor(schemas): add `videoUrl` and `thumbnailUrl`
- [ ] 🧹 chore: thumbnail placeholder generator hook
- [ ] 📝 docs: client usage & caching hints

## Day 14 – Delete Video with Play

- [ ] ✨ feat(storage): remove blobs when play deleted
- [ ] ✅ test(api): delete play removes storage object
- [ ] 🔨 refactor(repos): transactional delete pipeline (best-effort)
- [ ] 🧹 chore(logging): structured logs for storage ops
- [ ] 📝 docs: failure scenarios & retries (not guaranteed)

## Day 15 – Signed URLs (Secure Access)

- [ ] ✨ feat(storage): add signed URL generation (time-limited)
- [ ] ✅ test(storage): expiry honored; invalid keys rejected
- [ ] ✨ feat(api): `GET /v1/plays/{id}/video:signed`
- [ ] 🧹 chore(env): key/cred env validation
- [ ] 📝 docs: security trade-offs and TTL defaults

## Day 16 – Worker Service Skeleton

- [ ] ✨ feat(workers): add processing worker package (separate module)
- [ ] 🧹 chore(queue): define job schema for `process_video`
- [ ] ✅ test(workers): enqueue/dequeue with in-memory queue
- [ ] 🔨 refactor(app): emit job after successful upload
- [ ] 📝 docs: local dev loop for worker

## Day 17 – Frame Extraction

- [ ] ✨ feat(process): extract frames at N fps using OpenCV
- [ ] ✅ test(process): sample video → expected number of frames
- [ ] 🪄 perf(process): skip duplicate/near-identical frames
- [ ] 🧹 chore(media): temp scratch dir handling & cleanup
- [ ] 📝 docs: fps config & trade-offs

## Day 18 – Detection (Players & Ball)

- [ ] ✨ feat(ml): integrate YOLO model wrapper (players, ball)
- [ ] ✅ test(ml): detection smoke tests on sample frames
- [ ] 🪄 perf(ml): batch inference
- [ ] 🧹 chore(models): label map & confidence thresholds in config
- [ ] 📝 docs: model source, versioning, and reproducibility

## Day 19 – Diagram JSON Generation

- [ ] ✨ feat(process): convert detections → normalized diagram JSON
- [ ] ✅ test(process): geometry & timeline consistency checks
- [ ] 🔨 refactor(schemas): define `Diagram` schema + validation
- [ ] 🧹 chore: add sanitizers for outliers/missing frames
- [ ] 📝 docs: diagram schema contract

## Day 20 – Persist Diagram to Backend

- [ ] ✨ feat(api): `POST /v1/plays/{id}/diagram` (internal worker call)
- [ ] ✅ test(api): e2e—from video upload to stored diagram
- [ ] 🔨 refactor(repos): diagram store & retrieval abstraction
- [ ] 🧹 chore(security): internal auth or shared secret for worker
- [ ] 📝 docs: diagram lifecycle

## Day 21 – Serve Diagram (GET)

- [ ] ✨ feat(api): `GET /v1/plays/{id}/diagram` returns latest diagram
- [ ] ✅ test(api): 404 when missing; happy path for existing
- [ ] 🧹 chore(http): ETag/Last-Modified caching headers
- [ ] 🪄 perf(repos): projection-only read for large diagrams
- [ ] 📝 docs: client caching guidance

## Day 22 – Manual Diagram Edits (POST)

- [ ] ✨ feat(api): `POST /v1/plays/{id}/diagram:edit` accepts deltas
- [ ] ✅ test(api): schema-validated deltas; rejects invalid ops
- [ ] 🔨 refactor(services): merge engine for deltas
- [ ] 🧹 chore(audit): store editor + timestamp metadata
- [ ] 📝 docs: edit operations and invariants

## Day 23 – Diagram Validation Rules

- [ ] ✨ feat(schemas): strict validation rules (bounds, team sizes, frames)
- [ ] ✅ test(validation): boundary and edge cases
- [ ] 🔨 refactor(process): pre-validate worker output
- [ ] 🧹 chore: error taxonomy (user vs system)
- [ ] 📝 docs: validation spec

## Day 24 – Diagram Diffing & History

- [ ] ✨ feat(api): `GET /v1/plays/{id}/diagram:diff?from=&to=`
- [ ] ✅ test(api): diffs across versions; empty diff case
- [ ] 🔨 refactor(repos): versioned diagram storage
- [ ] 🧹 chore: migration note for versioning
- [ ] 📝 docs: diff format and examples

## Day 25 – E2E Tests (Play → Diagram)

- [ ] ✅ test(e2e): upload video → processed → diagram persisted → read back
- [ ] 🧹 chore(ci): run worker tests in pipeline
- [ ] 🧹 chore: test data fixtures for videos & expected diagrams
- [ ] 🪄 perf: parallelize test jobs
- [ ] 📝 docs: how to run e2e locally

## Day 26 – iOS App Skeleton (SwiftUI)

- [ ] ✨ feat(ios): create CourtIQ SwiftUI app project
- [ ] 🧹 chore(ios): set up bundle ids, targets, schemes
- [ ] ✨ feat(ios): basic app navigation shell (list → detail)
- [ ] 📝 docs(ios): build & run instructions

## Day 27 – iOS Plays List

- [ ] ✨ feat(ios): list view fetching `GET /v1/plays`
- [ ] ✅ test(ios): snapshot UI test for empty + populated lists
- [ ] 🔨 refactor(ios): data layer with async/await + decoding
- [ ] 🧹 chore(ios): environment config (base URL)
- [ ] 📝 docs(ios): API usage sample

## Day 28 – iOS Play Detail + Video

- [ ] ✨ feat(ios): detail screen with title/notes + video player
- [ ] 🔨 refactor(ios): caching for signed video URL
- [ ] ✅ test(ios): detail rendering with mock data
- [ ] 🧹 chore(ios): accessibility labels for key controls
- [ ] 📝 docs(ios): troubleshooting playback

## Day 29 – iOS Diagram Overlay

- [ ] ✨ feat(ios): render diagram overlay synced to video time
- [ ] 🪄 perf(ios): throttle redraw, reuse paths
- [ ] ✅ test(ios): unit tests for frame-to-time mapping
- [ ] 🔨 refactor(ios): diagram view model to parse JSON
- [ ] 📝 docs(ios): overlay architecture notes

## Day 30 – iOS Edit Metadata

- [ ] ✨ feat(ios): edit title/notes (PATCH) with optimistic UI
- [ ] ✅ test(ios): form validation and error states
- [ ] 🔨 refactor(ios): reusable API client + error mapping
- [ ] 🧹 chore(ios): loading/empty/error visuals
- [ ] 📝 docs(ios): UX patterns used

## Day 31 – AI Summary

- [ ] ✨ feat(ai): generate short play summary (rule/LLM hybrid or stub)
- [ ] ✅ test(ai): deterministic tests with fixtures/stubs
- [ ] ✨ feat(api): `GET /v1/plays/{id}/insights/summary`
- [ ] 🔨 refactor(services): insights service abstraction
- [ ] 📝 docs: assumptions & limitations

## Day 32 – Success/Failure Reasoning

- [ ] ✨ feat(ai): simple heuristics using diagram data (spacing, possession)
- [ ] ✅ test(ai): cases for success/failure classification
- [ ] ✨ feat(api): include reasoning in insights payload
- [ ] 🧹 chore: metrics counters for insights calls
- [ ] 📝 docs: feature flags to disable per-env

## Day 33 – Confidence Scores

- [ ] ✨ feat(ai): attach confidence per insight component
- [ ] ✅ test(ai): confidence ranges + aggregation tests
- [ ] 🔨 refactor(schemas): insights schema v1 with confidences
- [ ] 🧹 chore: serialize/rounding standards
- [ ] 📝 docs: interpretation guidance

## Day 34 – Serve Insights API

- [ ] ✨ feat(api): `GET /v1/plays/{id}/insights`
- [ ] ✅ test(api): insights endpoint integration tests
- [ ] 🧹 chore: caching headers & TTL for insights
- [ ] 🔨 refactor(services): batch compute on demand vs cached
- [ ] 📝 docs: endpoint examples

## Day 35 – Dockerize Backend

- [ ] ✨ feat(devops): add Dockerfile + .dockerignore
- [ ] 🧹 chore(devops): multi-stage build for slim image
- [ ] ✅ test(ci): docker build + healthcheck run
- [ ] 🪄 perf(devops): enable uvicorn workers via env
- [ ] 📝 docs: local docker run instructions

## Day 36 – CI/CD Backend

- [ ] ✨ feat(ci): GitHub Actions workflow (lint, test, build image)
- [ ] 🧹 chore(ci): cache deps, parallelize test matrix
- [ ] ✅ test(ci): required checks for PR merge
- [ ] 🧹 chore(ci): tag images by branch/commit
- [ ] 📝 docs: CI overview & secrets management

## Day 37 – Deploy Backend

- [ ] ✨ feat(devops): deploy to Cloud Run (or equivalent)
- [ ] 🧹 chore(devops): infra configs (service, concurrency, min instances)
- [ ] ✅ test(devops): smoke test deployed `/health`
- [ ] 🔨 refactor(config): production env and secrets wiring
- [ ] 📝 docs: rollout & rollback process

## Day 38 – TestFlight Build (iOS)

- [ ] ✨ feat(ios-devops): set up signing, app IDs, profiles
- [ ] 🧹 chore(ios-devops): fastlane lane for beta deploy (optional)
- [ ] ✅ test(ios-devops): archive build succeeds locally
- [ ] 🧹 chore(ios): app metadata + screenshots placeholders
- [ ] 📝 docs(ios-devops): TestFlight checklist

## Day 39 – Documentation Pass

- [ ] 📝 docs: expand README with API table and iOS setup
- [ ] 📝 docs: add `ROADMAP-HYBRID.md` reference and status
- [ ] 📝 docs: add troubleshooting & FAQ
- [ ] 🧹 chore: clean TODOs, rename ambiguous symbols
- [ ] 🧹 chore: tag v0.1.0 and generate changelog

## Day 40 – Bug Fix & Polish Buffer

- [ ] 🚑 fix: address top reported bugs from testing
- [ ] 💄 style: refine UI spacing/typography on iOS
- [ ] 🪄 perf: profile slow endpoints and optimize N+1s
- [ ] 🧹 chore: archive tech-debt items not in scope
- [ ] 📝 docs: “What’s next” and contribution welcome notes


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
