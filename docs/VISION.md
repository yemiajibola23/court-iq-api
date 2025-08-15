# CourtIQ — Product Vision

## Mission (North Star)
**Make basketball easier to learn — from day-one basics to advanced sets — through short clips, clear diagrams, and plain-English breakdowns anyone can follow and share.**

### What success looks like
- A user can **open a clip → understand the play** in **≤ 5 minutes** via labels, steps, and a quick explanation.
- People can **look up terms** (“Spain PnR”, “Horns”), see **what they mean**, and **watch an example**.
- Anyone (not just coaches) can **draw and share** a simple play.

---

## Who it’s for
- **Beginners & casual fans** — “What’s a horns set?” “What is Spain pick-and-roll?”
- **Youth players & rec hoopers** — learn fundamentals and a few go-to plays.
- **Coaches/analysts** — still benefit (clean management, diagrams), but they’re not the only audience.

---

## Product pillars
1) **Clarity** — short, friendly explanations; labeled diagrams; step-by-step “what & why”.
2) **Show + Tell** — clip + diagram + glossary terms woven together.
3) **Create & Share** — draw plays, save them, share a link.
4) **Reliable & Fast** — small, well-tested increments; quick responses.

---

## Core user journeys
1) **Explore & Learn**
   - Browse plays and glossary terms; filter by difficulty (Beginner / Intermediate / Advanced) and tags.
   - Open a clip and see a diagram and a **breakdown** of steps with timestamps.
2) **Manage content**
   - Create → List (filter/paginate) → View → **Delete** → Update metadata.
3) **Create & Share**
   - Draw a play, save as JSON/SVG, and get a public share link.

---

## Near-term feature scope
- **Plays CRUD**: POST/GET/GET list/**DELETE**, update metadata later.
- **List UX**: cursor pagination, title prefix filter, default/clamp limits, optional `hasMore`.
- **Glossary (Terms)**: searchable definitions with example clips and related terms.
- **Breakdowns**: a play’s step list with timecodes + short “why it works”.
- **Drawings**: simple stored diagrams with shareable slugs.
- **(Pipeline later)**: diagrams generated from video (frames → detection → diagram JSON).

---

## Data model sketch (incremental)
```json
// Play (existing)
{ "id": "uuid", "title": "Alpha Spain", "video_path": "https://...", "createdAt": "..." }

// Term (Glossary)
{
  "id": "uuid",
  "slug": "spain-pnr",
  "title": "Spain Pick-and-Roll",
  "definition": "A high PnR with a backscreen for the roller…",
  "tags": ["offense", "pnr"],
  "difficulty": "Intermediate",
  "example_play_ids": ["...","..."],
  "related_term_slugs": ["pick-and-roll","horns"]
}

// Breakdown (per Play)
{
  "id": "uuid",
  "play_id": "uuid",
  "steps": [
    {"t": 6.0, "label": "High PnR", "note": "5 screens for 1"},
    {"t": 9.5, "label": "Spain backscreen", "note": "2 backscreens 5’s defender"}
  ],
  "difficulty": "Intermediate"
}

// Drawing (for “draw & share”)
{
  "id": "uuid",
  "title": "Horns: Spain Variation",
  "payload": { /* shapes/players/paths JSON */ },
  "shared_slug": "xy7k3q",
  "is_public": true
}
```

**API surfaces (phased)**

-   **Plays**: POST /v1/plays, GET /v1/plays/{id}, GET /v1/plays (cursor+filter), **DELETE /v1/plays/{id}**.
-   **Terms (Glossary)**: GET /v1/terms, GET /v1/terms/{slug} (admin create/update later).
-   **Breakdowns**: GET /v1/plays/{id}/breakdown, PUT to save.
-   **Drawings**: POST /v1/drawings, GET /v1/drawings/{slug}.
-   **Search**: GET /v1/search?q=... (union over plays/terms; simple first).

**Roadmap snapshot (feature-first)**

-   **Day 9 --- Delete Play**: DELETE /v1/plays/{id} (204/404), tests, list reflects deletion.
-   **Day 10 --- Validation polish + list clamps**: video_path rules; default=10; clamp to [1,100]; optional hasMore.
-   **Day 11 --- SQLite migration**: swap in DB repo; keep interface; migrate CRUD.
-   **Day 12 --- Glossary MVP**: Term model + list/get + seed.
-   **Day 13 --- Breakdowns MVP**: store and serve steps per play.
-   **Day 14 --- Draw & Share (data layer)**: store drawing payload, retrieve by slug.

**Principles & non-goals (for now)**

-   **Principles**: clarity over configurability; privacy-safe by default; small, testable increments.
-   **Non-goals (v0.1)**: auth/roles, multi-team orgs, heavy editing UIs --- unless required for learning.

**How to use this doc**

-   Guides prioritization and scope decisions.
-   PRs should reference the relevant journey/pillar.
-   meta/plan.yml and ROADMAP.md should reflect this vision; our validators keep them aligned (current day is enforced strictly).