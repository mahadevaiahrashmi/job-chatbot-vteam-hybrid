---
agent-notes: { ctx: "walkthrough of complete sprint lifecycle sample", deps: [samples/full-sprint/docs/plans/sprint-1-plan.md, samples/full-sprint/docs/sprints/sprint-1-retro.md, samples/full-sprint/docs/code-reviews/sprint-1-review.md], state: active, last: "sato@2026-03-21" }
---

# Sample: full-sprint

**What this demonstrates:** A complete sprint lifecycle -- from product context through planning, TDD implementation, three-lens code review, done gate, and sprint boundary retrospective.

**Time to explore:** ~10 minutes

## Scenario

A user is building a URL shortener as a personal project. The methodology guided them through an entire sprint:

1. Pat documented the product context (what we are building and why)
2. Grace planned the sprint (three work items, sized and ordered)
3. Tara and Sato executed TDD on each item
4. Vik, Tara, and Pierrot reviewed the code through three independent lenses
5. Grace ran `/sprint-boundary` to close the sprint with a retrospective

## Timeline

This is the order in which events occurred, showing which agents were active at each step.

| Step | Phase | Agent(s) | Artifact |
|------|-------|----------|----------|
| 1 | Discovery | Cam, Pat | `docs/product-context.md` |
| 2 | Sprint Planning | Grace, Pat | `docs/plans/sprint-1-plan.md` |
| 3 | Implementation | Tara then Sato | _(code files not shown -- see hello-tdd sample)_ |
| 4 | Implementation | Tara then Sato | _(second work item)_ |
| 5 | Implementation | Tara then Sato | _(third work item)_ |
| 6 | Code Review | Vik, Tara, Pierrot | `docs/code-reviews/sprint-1-review.md` |
| 7 | Sprint Boundary | Grace, Pat, Wei | `docs/sprints/sprint-1-retro.md` |

## Files to Read (in order)

### 1. `docs/product-context.md`
Pat's product context document. This captures the human's intent, target users, success criteria, and non-negotiables. Pat wrote this during discovery (after Cam elicited the vision) and it serves as the reference for all product decisions during the sprint.

Notice:
- The success criteria are measurable, not vague ("under 50ms redirect latency" not "fast redirects")
- Non-negotiables are explicit constraints that override any other trade-off
- The document is concise -- Pat is terse and business-focused

### 2. `docs/plans/sprint-1-plan.md`
Grace's sprint plan. Three items sized S/S/M, with a velocity estimate and wave structure.

Notice:
- Items are ordered by dependency, not priority -- URL-1 must exist before URL-2 can work
- Each item has clear acceptance criteria (from Pat) and a TDD note
- The "Architecture Gate" column shows that no items in this sprint require the gate -- the tech decisions were simple enough to not trigger it

### 3. `docs/code-reviews/sprint-1-review.md`
The three-lens code review output. Vik reviewed for simplicity and maintainability, Tara reviewed test quality and coverage, and Pierrot reviewed for security concerns. All three ran in parallel.

Notice:
- **Three distinct voices.** Vik sounds like a veteran pushing back on cleverness. Tara is precise about coverage gaps. Pierrot finds the security issue nobody else noticed.
- **Severity levels matter.** Critical findings must be fixed before merge. Important findings should be fixed. Minor findings are suggestions.
- Pierrot found a real issue: the URL shortener was not validating input URLs, opening a redirect vulnerability. This was flagged Critical and fixed before the sprint closed.

### 4. `docs/sprints/sprint-1-retro.md`
The retrospective from `/sprint-boundary`. Grace facilitated, all agents contributed.

Notice:
- **What went well** captures process wins, not just feature completions
- **What did not go well** is honest -- the redirect vulnerability should have been caught earlier
- **Process improvements** are specific and actionable, not vague ("add URL validation to Tara's test checklist" not "be more careful about security")
- **Velocity** is tracked to calibrate future sprint planning

## Key Takeaway

A sprint is more than writing code. The methodology creates a trail of artifacts -- product context, sprint plan, code review, retrospective -- that provide traceability from "why are we building this" through "what did we learn." Each artifact is owned by a specific agent and follows a consistent format.
