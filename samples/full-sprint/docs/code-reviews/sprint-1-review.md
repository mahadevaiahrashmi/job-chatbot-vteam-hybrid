---
agent-notes: { ctx: "three-lens code review for sprint 1", deps: [samples/full-sprint/docs/plans/sprint-1-plan.md], state: active, last: "vik@2026-03-14" }
---

# Code Review -- Sprint 1

**Reviewed by:** Vik (simplicity), Tara (test quality), Pierrot (security)
**Date:** 2026-03-14
**Scope:** All code from URL-1, URL-2, URL-3

---

## Vik -- Simplicity and Maintainability

### Findings

**1. Short code generation is clean.** (Positive)
The `generate_short_code()` function is 8 lines, uses `secrets.token_bytes` for randomness, and encodes to base62. A junior dev could read this at 2am. No notes.

**2. The redirect handler does too much.** (Important)
`redirect_to_original()` handles the database lookup, the 404 case, the 301 response, and access logging in one function. This is fine at 20 lines, but it will grow. When you add click counting (it is in the out-of-scope list, so it is coming), this function becomes a mess.

Recommendation: extract the database lookup into a `get_link_by_code()` repository method now. The redirect handler should call it and handle only HTTP concerns. This is a 5-minute refactor that prevents a 30-minute untangling later.

_Severity: Important_

**3. Timestamp formatting is consistent.** (Positive)
All timestamps use ISO 8601 with UTC timezone. No local time ambiguity. Good.

### Summary

Clean, straightforward code. One structural improvement recommended. No cleverness detected -- that is a compliment.

---

## Tara -- Test Quality and Coverage

### Findings

**1. Happy-path coverage is solid.** (Positive)
All three items have tests for the primary success scenario. Test names describe behavior, not implementation. Assertions check response bodies, not just status codes. Good.

**2. Missing edge case: very long URLs.** (Important)
There is no test for URLs at the database column length limit. If someone shortens a 10,000-character URL, what happens? The implementation uses `TEXT` type in SQLite (no length limit), but the API layer might have a request body size limit from the framework. Add a test that submits a 8,192-character URL and verifies it round-trips through create and redirect.

_Severity: Important_

**3. Missing edge case: concurrent duplicate detection.** (Minor)
The duplicate detection test creates a link, then creates the same link again, and checks that the same short code is returned. But both operations are sequential. If two requests arrive simultaneously with the same URL, does the uniqueness constraint hold? At current scale (single user) this is theoretical, but the test should exist for correctness.

_Severity: Minor_

**4. Delete-then-redirect test exists.** (Positive)
Tara already wrote a test that creates a link, deletes it, and verifies the redirect returns 404. This cross-item integration test catches a real class of bugs.

### Summary

Coverage is good for a v1 sprint. Two gaps identified -- the long URL edge case should be addressed before merge, the concurrency test can wait.

---

## Pierrot -- Security

### Findings

**1. CRITICAL: No URL validation on create.** (Critical)
The create endpoint accepts any string that starts with `http://` or `https://`. This means an attacker can create a short link to `javascript:alert(1)` (which would fail the scheme check) but can create `https://evil.com/phishing-page` which is fine -- that is the point of a URL shortener. More concerning: there is no check for `file://`, `data:`, or other schemes that could slip through if the validation regex is loosened later.

But the real issue: the endpoint does not validate that the URL is well-formed beyond the scheme check. `https://` (with nothing after it) is accepted. `https://[malformed` is accepted. These create short links that redirect to broken or potentially dangerous destinations.

Recommendation: Use Python's `urllib.parse.urlparse` and verify that the result has a non-empty `netloc` component. This catches malformed URLs without being overly restrictive.

_Severity: Critical -- must fix before merge_

**2. Short codes use cryptographic randomness.** (Positive)
`secrets.token_bytes` is the correct choice. Not `random.randint`, not `uuid4().hex[:6]`. Someone read the docs. I am pleasantly surprised.

**3. No rate limiting on create endpoint.** (Minor)
A single user app, so this is low risk. But if the app is ever exposed without authentication, someone could exhaust the short code space (56 billion codes, but still). Note for v2: add rate limiting if auth is added.

_Severity: Minor_

### Summary

One critical finding: URL validation is insufficient and must be fixed. The redirect is a clean 301 with no JavaScript (good -- matches the non-negotiables). Cryptographic randomness for short codes is correct. Overall security posture is reasonable for a personal tool, with the URL validation fix.

---

## Action Items

| # | Finding | Severity | Owner | Status |
|---|---------|----------|-------|--------|
| 1 | Extract `get_link_by_code()` repository method | Important | Sato | Fixed |
| 2 | Add long URL edge case test | Important | Tara | Fixed |
| 3 | Fix URL validation (require valid netloc) | Critical | Sato | Fixed |
| 4 | Add concurrent duplicate detection test | Minor | Tara | Deferred to sprint 2 |
| 5 | Consider rate limiting for v2 | Minor | Pat (backlog) | Logged |

All Critical and Important items were resolved before the sprint closed.
