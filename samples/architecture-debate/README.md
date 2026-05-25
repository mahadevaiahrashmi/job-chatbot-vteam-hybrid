---
agent-notes: { ctx: "walkthrough of architecture debate sample", deps: [samples/architecture-debate/docs/adrs/0001-storage-backend.md, samples/architecture-debate/docs/tracking/2026-03-15-notes-app-debate.md], state: active, last: "sato@2026-03-21" }
---

# Sample: architecture-debate

**What this demonstrates:** The Architecture Gate -- Archie proposes a design and writes an ADR, Wei challenges it through multi-round adversarial debate, and the ADR is updated to reflect the outcome.

**Time to explore:** ~5 minutes

## Scenario

A user is building a personal note-taking app. Archie proposed using SQLite for storage. Before any implementation code could be written, the Architecture Gate required:

1. Archie wrote an ADR documenting the decision and trade-offs
2. Wei challenged the decision as a standalone agent (this is mandatory -- skipping Wei is a process violation)
3. A multi-round debate was executed and tracked
4. The ADR was updated to reflect insights from the debate
5. The human approved the architecture

## Files to Read (in order)

### 1. `docs/adrs/0001-storage-backend.md`
The Architecture Decision Record. This is the final version -- after the debate with Wei. Notice:

- **Status is "Accepted"** -- the gate has passed, implementation can proceed
- **The decision section** explains *why* SQLite, not just *what*
- **The "Debate Summary" section** at the bottom captures how Wei's challenges improved the decision. Wei raised the multi-device sync concern, and Archie acknowledged it as a consequence rather than dismissing it
- **A consequence was added** ("migration path to PostgreSQL") that was not in Archie's original draft -- Wei's challenge directly improved the ADR

### 2. `docs/tracking/2026-03-15-notes-app-debate.md`
The full debate transcript. This is the structured back-and-forth that the Architecture Gate requires. Notice:

- **Round 1:** Wei's challenges are numbered and specific -- not vague objections but pointed questions about real failure modes
- **Round 2:** Archie responds to each challenge individually, conceding where Wei has a point and defending where the trade-off is acceptable
- **Resolution:** Clear summary of what was resolved, what remains as an accepted risk, and what changed in the ADR

## Key Takeaway

The Architecture Gate exists to make decisions stronger, not to slow things down. Wei's challenge about multi-device sync did not change the SQLite decision -- but it did cause Archie to add a migration path consequence and document the sync limitation explicitly. Without the debate, that gap would have been discovered during implementation or, worse, by users.
