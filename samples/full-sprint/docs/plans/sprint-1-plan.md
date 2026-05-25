---
agent-notes: { ctx: "sprint 1 plan for URL shortener", deps: [samples/full-sprint/docs/product-context.md], state: active, last: "grace@2026-03-11" }
---

# Sprint 1 Plan -- linkr

**Sprint goal:** A working URL shortener that can create short links and redirect visitors.
**Sprint dates:** 2026-03-11 to 2026-03-14
**Velocity estimate:** 6 points (first sprint -- conservative baseline)
**Planned points:** 5

## Items

| ID | Title | Size | Points | Arch Gate? | Dependencies |
|----|-------|------|--------|------------|--------------|
| URL-1 | Create short link | S | 1 | No | None |
| URL-2 | Redirect to original URL | S | 2 | No | URL-1 |
| URL-3 | List and delete links | M | 2 | No | URL-1 |

## Wave Structure

**Wave 1:** URL-1 (create short link) -- must complete first because URL-2 and URL-3 depend on links existing.

**Wave 2:** URL-2 and URL-3 in parallel -- these are independent of each other (redirect does not depend on list/delete, and vice versa).

## Item Details

### URL-1: Create short link (S)

**Acceptance criteria (Pat):**
- POST `/api/links` with `{"url": "https://example.com/long-path"}` returns `{"short_code": "abc123", "short_url": "https://yourdomain.tld/abc123"}`
- Short code is 6 characters, base62 (a-z, A-Z, 0-9)
- Duplicate URL returns the existing short code, not a new one
- Invalid URL (not http/https) returns 400 with error message

**TDD plan:** Tara writes tests for valid URL creation, duplicate detection, and invalid URL rejection. Sato implements.

### URL-2: Redirect to original URL (S)

**Acceptance criteria (Pat):**
- GET `/{short_code}` returns 301 redirect to the original URL
- Unknown short code returns 404
- Redirect latency under 50ms (p99)

**TDD plan:** Tara writes tests for successful redirect, unknown code, and response code verification. Sato implements.

### URL-3: List and delete links (M)

**Acceptance criteria (Pat):**
- GET `/api/links` returns all links with short codes, original URLs, and creation timestamps
- DELETE `/api/links/{short_code}` removes the link and returns 204
- DELETE for unknown code returns 404
- After deletion, the short code returns 404 on redirect

**TDD plan:** Tara writes tests for list (empty, one item, multiple items), delete success, delete unknown, and redirect-after-delete. Sato implements.

## Risks

- First sprint -- velocity estimate is a guess. We may over- or under-commit.
- No Architecture Gate items this sprint. If the SQLite schema turns out to need rework, that is sprint 2 tech debt.
