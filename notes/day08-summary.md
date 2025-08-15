# Day 8 Summary — CourtIQ (Backend)

## Objective
GET /v1/plays with pagination & title filter

## What shipped
- **GET `/v1/plays`** route with `limit`, `cursor`, `title` (prefix, case-insensitive)
- Repo **`list_plays(cursor, limit, title_prefix)`**: filter-then-paginate over stable insertion order
- **400 Invalid cursor** when the cursor isn’t in the filtered view
- Centralized **Play → DTO** mapping in router

## Tests added
- Pagination happy path (3 pages)
- Title prefix filter (happy path)
- Filtered pagination (cursor within subset)
- Edge cases: empty results, cursor at end, bad cursor (400)

## Tech Debt
- **Resolved:** TD8 (test isolation), TD16 (route path normalization), TD17 (DTO mapper)
- **Added:** TD13 (repo DI), TD14 (opaque/composite cursor after DB), TD15 (hasMore), TD18 (limit default/clamp tests)

## Notes
- IDs are UUIDv4; ordering uses dict insertion order (stable in Py ≥3.7)
- Cursor = last returned `id`
- `nextCursor` = `null` when no more results
