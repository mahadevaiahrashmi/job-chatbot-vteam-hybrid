---
agent-notes: { ctx: "sprint 1 retrospective for URL shortener", deps: [samples/full-sprint/docs/plans/sprint-1-plan.md, samples/full-sprint/docs/code-reviews/sprint-1-review.md], state: active, last: "grace@2026-03-14" }
---

# Sprint 1 Retrospective -- linkr

**Sprint dates:** 2026-03-11 to 2026-03-14
**Facilitated by:** Grace
**Participants:** Sato, Tara, Vik, Pierrot, Pat

## Velocity

- **Planned:** 5 points (URL-1: 1, URL-2: 2, URL-3: 2)
- **Completed:** 5 points (all items done)
- **Baseline velocity:** 5 points per sprint (single data point -- will refine over 3 sprints)

## What Went Well

1. **TDD caught a design issue early.** When Tara wrote the tests for URL-2 (redirect), she included a test for the 301 status code specifically. Sato's first implementation returned 302 (temporary redirect). The test caught it immediately. A 302 would have caused browsers to re-check the shortener on every visit instead of caching the redirect -- a subtle performance and correctness bug that TDD surfaced before it shipped.

2. **Wave structure worked.** URL-1 completed in wave 1, then URL-2 and URL-3 ran in parallel in wave 2. This saved approximately one session of sequential work. For a 3-item sprint the benefit is modest, but the pattern scales.

3. **Product context document prevented scope creep.** Sato started adding click counting to the redirect handler ("it is just one line"). Pat pointed to the product context: "No analytics or tracking" is a non-negotiable, and click counting is explicitly out of scope. The line was removed. Without the product context doc, this would have been a 20-minute debate instead of a 20-second reference.

## What Did Not Go Well

1. **URL validation gap reached code review.** Pierrot found that malformed URLs were accepted by the create endpoint. This should have been caught earlier -- either by Tara (input validation is an unhappy path) or by Sato (boundary validation is his responsibility). The fix was small, but the gap surviving until code review means the TDD red phase missed a category of input.

2. **Velocity estimate was a guess.** We planned 5 points against a 6-point estimate, but we had no prior data. The sprint completed in 3 days, which means either the items were oversized or the velocity estimate was too conservative. Need more data points.

## Process Improvements

1. **Add URL/input validation to Tara's test checklist.** For any endpoint that accepts user input, Tara should explicitly test: malformed input, empty input, oversized input, and input with unexpected schemes/protocols. This is a standing checklist item for all future API work.

2. **Track "found in review" defects.** Pierrot's URL validation finding was caught in review, not in TDD. We should track how many issues are caught at each phase (TDD vs. code review vs. production). If code review is consistently catching input validation issues, the TDD red phase has a blind spot.

3. **Do not estimate velocity from one sprint.** Use the first three sprints to establish a range, then use the average. Sprint 1 velocity of 5 is a data point, not a baseline.

## Items for Next Sprint (Grace's Recommendation to Pat)

- URL-4: Custom short codes (allow user to choose `my-link` instead of `abc123`)
- URL-5: Link expiration (optional TTL on short links)
- URL-6: API authentication (required before exposing to the internet)

Pat to prioritize. Grace recommends URL-6 first -- the app is currently open to anyone who knows the URL, and Pierrot flagged the lack of rate limiting. Auth before exposure.

## Sprint Health

| Metric | Value | Notes |
|--------|-------|-------|
| Items planned | 3 | |
| Items completed | 3 | |
| Items deferred | 0 | |
| Critical review findings | 1 | URL validation -- fixed |
| Important review findings | 2 | Both fixed |
| Tech debt logged | 0 | Clean sprint |
| Process violations | 0 | |
