---
agent-notes: { ctx: "HVE Core learnings for agent system evolution", deps: [docs/methodology/personas.md, docs/process/team-governance.md], state: active, last: "coordinator@2026-03-02" }
---

# What We Learn from HVE Core

> **Source:** [microsoft/hve-core](https://github.com/microsoft/hve-core) (Hypervelocity Engineering Core)
> **Reviewed:** 2026-03-02
> **Status:** Research — not yet implemented

HVE Core is Microsoft's enterprise-grade prompt engineering framework for GitHub Copilot. It features 35 specialized agents, a constraint-based RPI (Research → Plan → Implement → Review) methodology, and a plugin architecture. This doc captures learnings that could improve our agent system.

## High-Impact Learnings

### 1. Explicit Negative Constraints on Agents

**What HVE does:** Every agent definition includes explicit "cannot do" constraints. The `task-researcher` says "never implement code." The `task-planner` says "never write implementation code." These are separate from tool restrictions.

**What we do:** Our agents define allowed tools (which implicitly constrains) but don't state explicit negative boundaries in the agent definition text itself.

**Why it matters:** Claude drifts outside its lane when boundaries are implicit. Explicit negative constraints are a stronger signal than the absence of a tool. A researcher with no `Write` tool might still suggest code inline — but one that says "you never suggest implementation" won't.

**Proposed change:** Add a `## Constraints` section to each agent definition listing 3-5 things the agent must never do. Examples:
- Archie: "Never writes implementation code. Never skips Wei challenge."
- Tara: "Never implements production code. Never approves without running tests."
- Cam: "Never makes technical decisions. Never implements."
- Sato: "Never writes tests before Tara. Never skips the plan."

### 2. Evidence-Based Decision Tracing

**What HVE does:** Every planning decision must trace back to research with exact file path + line number references. Plans reference research findings as `path/to/file.md:42`. The implementation phase tracks which plan items it executed and which it deviated from.

**What we do:** Our ADR process captures decisions and rationale, but doesn't enforce a citation chain from research → plan → implementation.

**Why it matters:** This is HVE's core innovation. When the AI knows it must cite sources with line numbers, it stops hallucinating plausible answers and starts verifying. It shifts the optimization target from "sounds right" to "is right."

**Proposed change:** Update the Architecture Gate to require that ADR "Context" sections cite specific files and line numbers. Update Archie's agent definition to enforce this.

### 3. Discrepancy Logging

**What HVE does:** A planning log tracks deviations between what was planned and what was actually implemented, with reasons for each deviation. This lives in `.copilot-tracking/plans/logs/`.

**What we do:** Our Done Gate checks completion but doesn't capture the delta between plan and reality. Retros capture learnings but not per-item deviations.

**Why it matters:** Discrepancy logs catch scope drift in real time, feed better retros, and create a historical record of why plans change. They also help calibrate future planning — if plans always deviate in the same ways, the planning process needs adjustment.

**Proposed change:** Add a discrepancy section to sprint plan docs (`docs/sprints/sprint-N-plan.md`). Grace or Sato logs deviations as they occur. Retro skill reads the log.

### 4. Research as a Distinct Phase

**What HVE does:** Research is a standalone phase before planning. A dedicated `task-researcher` agent investigates the problem space, documents findings with evidence, evaluates alternatives, and produces a research artifact. The planner then consumes this artifact.

**What we do:** Our Phase 1 (Discovery) is led by Cam and focuses on vision elicitation — understanding *what* the user wants. Technical investigation happens implicitly during Phase 2 (Architecture) when Archie needs to understand the problem space before writing ADRs.

**Why it matters:** Combining technical research with architecture design creates cognitive load. Archie has to both investigate and decide simultaneously. A separate research step would let Archie consume pre-verified findings rather than doing ad-hoc investigation mid-ADR.

**Proposed change:** Consider adding a Phase 1.5 (Research) between Discovery and Architecture for technically complex projects. Could be led by an Explore agent or a new researcher persona. Output: a research artifact that Archie consumes.

### 5. Subagent Delegation for Parallel Execution

**What HVE does:** The `task-implementor` doesn't execute directly. It orchestrates `phase-implementor` subagents, each handling one phase of the plan. Independent phases run in parallel. The orchestrator tracks progress and handles failures.

**What we do:** Sato does both orchestration and execution. Grace handles parallel work distribution at the sprint level, but within a single work item, Sato executes sequentially.

**Why it matters:** For large work items with independent subtasks, subagent delegation enables parallelism within a single item, not just across items. It also creates cleaner failure domains — one subagent failing doesn't poison the orchestrator's context.

**Proposed change:** For M+ items, Sato could delegate to parallel implementation subagents. This would require Grace to coordinate at a finer grain. Worth prototyping on a complex implementation.

### 6. Structured Session State

**What HVE does:** All state lives in `.copilot-tracking/` with date-stamped subdirectories:
- `.copilot-tracking/research/YYYY-MM-DD/` — research artifacts
- `.copilot-tracking/plans/YYYY-MM-DD/` — implementation plans
- `.copilot-tracking/changes/YYYY-MM-DD/` — change records (files added/modified/removed)
- `.copilot-tracking/reviews/YYYY-MM-DD/` — review findings
- `.copilot-tracking/memory/` — session persistence

**What we do:** We use `.claude/handoff.md` for session handoffs, `docs/sprints/` for sprint plans, and `docs/retrospectives/` for retros. Tracking artifacts are in `docs/tracking/`.

**Why it matters:** HVE's approach makes every session fully auditable and resumable. The date-stamped directory structure means artifacts never collide and the history is browsable. Our approach works but is more scattered.

**Proposed change:** Consider consolidating tracking artifacts under a single directory with date-stamped subdirectories. Not urgent — our current approach works, but consolidation would improve discoverability.

## Medium-Impact Learnings

### 7. Memory Agent for Session Persistence

HVE has a dedicated `memory` agent that manages session persistence, context recovery, and checkpoint/resume workflows. Our `/handoff` and `/resume` commands cover similar ground, but a dedicated agent could handle mid-session context recovery (e.g., after a `/clear` or context compression) more gracefully.

### 8. Prompt Engineering as First-Class Capability

HVE has a `prompt-builder` agent with a dual-persona system (creator + validator) and automated testing via a `prompt-tester` subagent. If our projects involve writing prompts or agent definitions, a meta-capability for creating, validating, and testing prompt artifacts would be valuable. This is particularly relevant for template maintenance.

### 9. Design Thinking as Structured Methodology

HVE implements a 9-method Design Thinking framework (Scope → Research → Synthesis → Brainstorming → Concepts → Lo-Fi Prototypes → Hi-Fi Prototypes → Testing → Iteration at Scale) with dedicated coaching agents. Our Cam + Dani cover similar ground but informally. Structured DT methods could improve Discovery phase quality for user-facing products.

### 10. Schema Validation for Agent Definitions

HVE validates all agent, instruction, and prompt frontmatter against JSON schemas in CI. Our agent-notes protocol is manually enforced. Schema validation would catch malformed agent definitions before they cause runtime issues.

## Already Well-Covered

These areas are handled equivalently or better by our current system:

| Area | HVE Approach | Our Approach | Assessment |
|------|-------------|--------------|------------|
| Adversarial review | Single architecture reviewer | Wei + Architecture Gate with multi-round debate | Ours is stronger |
| TDD | Implied in implementation phase | Tara → Sato pipeline with explicit red-green-refactor | Equivalent |
| Code review | Single PR reviewer with 8 dimensions | Vik + Tara + Pierrot triple-lens | Ours is stronger |
| Board enforcement | Status tracking in files | Ordered lifecycle with Grace enforcement | Equivalent |
| Veto power | Not explicit | Tara (tests) + Pierrot (security/compliance) with escalation | Ours is stronger |
| Sprint management | Not covered (project-level focus) | Grace with sprint boundary workflow | Ours is stronger |
| Proxy mode | Not covered | Pat with guardrails and logging | Unique to us |

## Implementation Priority

If we decide to implement, suggested order:

1. **Negative constraints on agents** — Low effort, high impact, no structural changes
2. **Evidence-based tracing in ADRs** — Medium effort, high impact on architecture quality
3. **Discrepancy logging** — Low effort, improves retro quality
4. **Research sub-phase** — Medium effort, only needed for complex projects
5. **Subagent delegation** — High effort, only valuable for large work items
6. **Structured session state** — Medium effort, nice-to-have consolidation
