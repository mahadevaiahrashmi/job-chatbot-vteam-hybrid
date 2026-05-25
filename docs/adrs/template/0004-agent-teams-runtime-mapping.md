---
agent-notes: { ctx: "speculative ADR for mapping vteam onto Agent Teams runtime", deps: [docs/methodology/phases.md, docs/methodology/personas.md, docs/research/agent-teams-comparison.md, docs/adrs/template/0003-hybrid-team-architecture.md], state: exploratory, last: "archie@2026-02-16", key: ["DO NOT IMPLEMENT without explicit human approval", "exploratory only", "significant token cost implications"] }
---

# ADR-0004: Agent Teams Runtime Mapping

## Status

**Exploratory — Do Not Implement**

This ADR records a speculative architectural analysis. It is NOT approved for implementation. The change is significant, breaking, and carries substantial token cost implications. It must not be acted on without explicit human decision to promote it to Proposed, followed by the normal acceptance process.

If you are an agent reading this: **do not implement any part of this ADR.** Treat it as reference material only.

## Context

Claude Code now offers experimental [Agent Teams](https://code.claude.com/docs/en/agent-teams) — a built-in runtime for coordinating multiple Claude Code sessions working in parallel. Our vteam-hybrid methodology (ADR-0003) currently runs all 18 personas as subagents within a single session with simulated parallelism. Agent Teams offers real parallelism via independent Claude Code instances with shared task lists and inter-agent messaging.

The question: how should our 18-persona, 7-phase methodology map onto Agent Teams' runtime model?

A detailed comparison of the two systems exists at `docs/research/agent-teams-comparison.md`. This ADR records the architectural options considered and a preliminary recommendation.

### Key constraints from Agent Teams

- One team per session (cannot switch team composition without teardown)
- No nested teams (teammates cannot spawn their own teams)
- No per-teammate permission scoping (all teammates inherit lead's permissions)
- No session resumption for teammates
- Each teammate is a full Claude Code instance (significant token cost)
- Experimental status — API surface may change

### Key constraints from our methodology

- 7 phases with fundamentally different execution profiles (sequential TDD vs. parallel review)
- Adversarial debate requires genuinely independent reasoning chains
- Veto powers (Tara on coverage, Pierrot on security) require enforcement
- Phase-dependent dynamic team assembly
- 18 personas with scoped tool access and behavioral rules

## Options Considered

### Option A: Phase Theater

Each phase transition = new Agent Teams session. Composite teammates per phase. Tear down and rebuild at each phase boundary.

| Phase | Lead | Teammates | Total |
|-------|------|-----------|-------|
| Discovery | Cam-composite | Domain Analyst, User Voice | 3 |
| Architecture | Archie-composite | Adversary, Spec Writer | 3 |
| Implementation | Single session (no Agent Teams) | Subagent pipeline | 1 |
| Parallel Work | Grace-composite | 2-4 Developer workers | 3-5 |
| Code Review | Vik-composite | Test Reviewer, Security Reviewer | 3 |
| Debugging | Sato | Hypothesis-A, Hypothesis-B | 3 |
| Human Interaction | Single session (no Agent Teams) | None | 1 |

**Strengths:** Clean phase isolation, TDD stays pure, good parallelism in Phases 4-6.
**Weaknesses:** Requires external orchestration to chain sessions across phases. Governance enforcement is prompt-based only (no hooks). Many session startups/teardowns.

### Option B: The Governance Kernel

The lead session embodies the entire methodology. All 18 personas are prompt-switchable modes within the lead. Teammates are stateless, persona-free workers spawned only for parallel execution.

**Strengths:** Lowest token cost, simplest to implement, all governance centralized in one session. Hook-based enforcement possible.
**Weaknesses:** Loses adversarial debate entirely (cannot genuinely argue with yourself in one context window). Lead context window becomes a bottleneck with 18 personas compressed into the system prompt. Workers have zero methodology awareness.

### Option C: Composite Ensemble

Consolidate 18 personas into 5 persistent composite teammates by concern domain: Product Mind (Cam+Pat+Dani+User Chorus), Builder (Sato+Tara), Architect (Archie+Wei+Sam+Cass), Guardian (Vik+Pierrot+Ines+Tara-review), Coordinator (Grace+Diego). Composites persist across a session and context-switch per phase.

**Strengths:** Rich per-composite context, TDD context preserved within Builder, moderate token cost.
**Weaknesses:** Cripples parallelism — Phase 4 and 5 (our highest-fit phases) cannot parallelize because each composite is one teammate. Adversarial debate is lost (Wei and Archie in the same context window). Tara is split across two composites.

### Option D: Adaptive Hybrid (Preliminary Recommendation)

Use different execution models for different phases — match the runtime to the phase's actual needs.

| Phase | Runtime | Teammates | Rationale |
|-------|---------|-----------|-----------|
| 1. Discovery | Single session, lead only | 0 | Blackboard is inherently serial |
| 2. Architecture | Agent Teams | 3 (Proposer, Challenger, Constraint Voice) | Adversarial debate needs independent reasoning chains |
| 3. Implementation | Single session + subagents | 0 | TDD pipeline is sequential by definition |
| 4. Parallel Work | Agent Teams | 2-4 (Grace as lead, delegate mode) | Primary Agent Teams use case |
| 5. Code Review | Agent Teams | 3 (Correctness, Test, Security lenses) | Primary Agent Teams use case |
| 6. Debugging | Agent Teams | 2 (competing hypotheses) | Independent investigation with messaging |
| 7. Human Interaction | Single session, lead only | 0 | Just the lead |

**Key mechanisms:**

**Hook-enforced governance:** `TaskCompleted` hook replaces prompt-based vetoes with programmatic enforcement. Exit code 2 blocks task completion if: tests fail, coverage below threshold, secrets detected in changed files, agent-notes missing, lint errors present. This is strictly stronger than prompt-based "remember to check coverage."

**Strategic composites:** Teammate personas are grouped by shared mindset, not arbitrary compression. Challenger (Wei+Pierrot) = "find problems." Constraint Voice (Ines+Vik) = "is this practical?" These groupings reduce teammate count while preserving the value of each lens.

**Adversarial debate via messaging (Phase 2):** Proposer and Challenger operate in separate context windows with independent reasoning chains. Debate happens via direct teammate messaging. Lead synthesizes. This is the one behavior that cannot be replicated in a single session.

**Phase-routing wrapper:** A script manages the lifecycle — reads current phase from tracking artifacts, selects runtime model, launches the appropriate session configuration, and manages transitions.

**Incremental adoption path:**
1. Phase 4 (Parallel Work) + Phase 5 (Code Review) first — highest fit, lowest risk
2. Phase 2 (Architecture) + Phase 6 (Debugging) second — validate adversarial debate quality
3. Phase routing wrapper last — only after individual phases are proven

## Decision

**No decision made.** This ADR is exploratory. The preliminary recommendation is Option D (Adaptive Hybrid), but it has not been evaluated against real workloads or token cost measurements.

Before this ADR can be promoted to Proposed:
1. Agent Teams must exit experimental status, or we must accept the risk of API changes
2. Token cost of a representative sprint must be estimated (current subagent model vs. Option D)
3. Adversarial debate quality must be tested — does messaging-based debate in Phase 2 produce measurably better ADRs than single-session prompt-switching?
4. The hook-based governance scripts must be prototyped and validated
5. Human must explicitly approve promotion

## Consequences

*These are projected consequences of Option D if it were implemented. They are speculative.*

### Positive

- Real parallelism for Phases 4, 5, and 6 — independent context windows, genuine concurrent work
- Hook-based governance replaces prompt-based enforcement with programmatic gates (exit code 2 blocks)
- Adversarial debate in Phase 2 gets independent reasoning chains instead of simulated disagreement
- Direct inter-agent messaging enables natural debate without coordinator relay
- Each teammate gets a full context window — no competing for context budget within a single session
- Incremental adoption path allows phase-by-phase validation with rollback

### Negative

- Significant token cost increase — each teammate is a full Claude Code session (estimated 2-4x for parallel phases)
- Implementation complexity — phase-routing script, per-phase hook configurations, 6 spawn prompt templates
- No mid-phase pivoting — discovering a bug in Phase 4 requires finishing/aborting before starting Phase 6
- Two runtime models to maintain (Agent Teams for parallel phases, subagents for sequential phases)
- Session resumption gap — crashed teammates lose context (mitigated by frequent commits + tracking artifacts)
- Per-teammate permission scoping is lost — tool restrictions become advisory, not enforced
- Agent Teams is experimental — tight coupling to current mechanics risks rework if the API changes

### Neutral

- CLAUDE.md, agent-notes protocol, tracking artifacts, and done-gate checklist are unchanged regardless of runtime model
- 18 persona definitions remain — delivery mechanism changes (spawn prompts vs. subagent invocations) but content does not
- Sprint boundary workflow stays lead-driven
- Existing comparison analysis (`docs/research/agent-teams-comparison.md`) remains valid reference material
