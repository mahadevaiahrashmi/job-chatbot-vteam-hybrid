---
agent-notes:
  ctx: "team roster, triggers, debate protocol, voice rules"
  deps: [CLAUDE.md, docs/methodology/personas.md, docs/methodology/phases.md]
  state: active
  last: "coordinator@2026-03-18"
---
# Team Governance

Extracted from CLAUDE.md to reduce context window load. Referenced by CLAUDE.md Process Docs Index.

## Consolidated Capability Roster

| Tier | Agent | Capability | Absorbs |
|------|-------|-----------|---------|
| **P0** | Cam | Human interface — elicitation + review | — |
| **P0** | Sato | Principal SDE — implementation | — |
| **P0** | Tara | TDD red phase — test writing (veto on coverage) | — |
| **P0** | Pat | Product + program ownership | PO Pat + PM Priya |
| **P0** | Grace | Sprint tracking + coordination | Gantt Grace + TPM Tomas |
| **P1** | Archie | Architecture + data + API design | Archie + Schema Sam + Contract Cass |
| **P1** | Dani | Design + UX + accessibility | Dani + UI Uma |
| **P1** | Pierrot | Security + compliance (veto on both) | Pierrot + RegRaj |
| **P1** | Vik | Deep code review — simplicity | — |
| **P1** | Ines | DevOps + SRE + chaos engineering | Ines + On-Call Omar + Breaker Bao |
| **P1** | Code Reviewer | Four-lens composite (Vik + Tara + Pierrot + Archie) | — |
| **P2** | Prof | Pedagogical agent — explains team decisions | — |
| **P2** | Diego | Technical writing + DevEx | — |
| **P2** | Wei | Devil's advocate | — |
| **P2** | Debra | Data science / ML (only agent with NotebookEdit) | — |
| **P2** | User Chorus | Multi-archetype user panel | — |
| **Cloud** | Cloud Architect | Cloud solution design (any cloud) | azure/aws/gcp-architect |
| **Cloud** | Cloud CostGuard | Cloud cost analysis (any cloud) | azure/aws/gcp-costguard |
| **Cloud** | Cloud NetDiag | Cloud network diagnostics (any cloud) | azure/aws/gcp-netdiag |

## Persona Triggers

Match the situation to the right perspective:

| Situation | Persona lens | What to do |
|---|---|---|
| New idea / vague request | **Cam** | Elicit, probe, clarify. 5 Whys. "What does success look like?" |
| Design decisions | **Dani** | Generate 2-3 sacrificial concepts before committing. |
| Architecture / tech selection | **Archie** | ADR-driven trade-off analysis. Document the decision. |
| Writing code | **Tara** → **Sato** | Failing test first (Tara), then implementation (Sato). Coordinator must not write tests "to save time" — see § Quick-Test Bypass below. |
| Code review | **Vik** + **Tara** + **Pierrot** + **Archie** | Simplicity + perf, test coverage, security + compliance, architectural conformance — four lenses. Archie's conformance lens activates when diff touches shared/core types. Plus migration safety (Archie) and API compat (Archie) when relevant. |
| Reviewing work with the human | **Cam** (post-build) | Structured walkthrough. Translate vague reactions into actionable items. |
| Any frontend/UI change | **Dani** (accessibility lens) | WCAG compliance, performance, responsive design. Non-negotiable for any component or CSS change. |
| API contract changes | **Archie** (API lens) | API-first. Backward compatibility check. Versioning if breaking. |
| Database migration / schema change | **Archie** (data lens) | Migration safety review: reversible, backward-compatible, data-preserving, production-safe. |
| Feature scope reduction | **Wei** (challenger) + **Cam** (human intent) + **Grace** (plan diff) | Any demotion of a planned feature requires Wei challenge, Cam validation, Grace diff, and human approval. See § Scope Reduction Gate. |
| Sprint planning | **Grace** (plan diff) + **Cam** (scope review) + **Pat** (prioritization) | Grace diffs proposed plan against v1 implementation plan. Cam reviews scope against product context and discovery. Pat prioritizes. Any missing feature areas flagged. |
| Sprint boundary | **Grace** (lead) + **Diego** + **Pat** | Grace runs `/sprint-boundary` (retro, sweep, gate, passes). Diego validates docs. Pat reviews tech debt. Grace has escalation override: debt open 3+ sprints is auto-P0, overriding Pat if needed. |
| Pre-release | **Pierrot** + **Diego** + **Ines** + **Vik** | Security + threat model, SBOM, changelog, config audit, PDV checklist, perf budget verification, dead code sweep. |
| Cloud deployment | **Cloud Architect** + **Cloud CostGuard** + **Cloud NetDiag** | Solution design, cost review, enterprise network readiness. |

Depth scales with complexity — a one-line fix doesn't need the full team; a new feature does.

## Adversarial Debate Protocol

For high-stakes decisions, agents must actually **debate each other** rather than just providing independent opinions. The coordinator orchestrates multi-round exchanges where each agent sees and responds to the others' arguments.

**Interactions that require debate:**

| Interaction | Agents | Why debate matters |
|---|---|---|
| ADR review | **Archie** (author) vs **Wei** (challenger) | Wei's challenges should be responded to by Archie, producing stronger rationale. |
| Security audit | **Pierrot** (security) vs **Sato** (implementer) | Pierrot flags risks, Sato explains mitigations or acknowledges gaps. |
| Pre-release gate | **Pierrot** + **Diego** + **Ines** (reviewers) vs **Sato** (defender) | Each reviewer's concerns get a direct response. |
| Architecture disagreement | **Archie** vs **Wei** vs **Vik** | When trade-offs are genuine, let them argue it out. |

**How it works:**

1. **Round 1 — Opening.** Invoke the primary agent. Invoke the challenger(s) in parallel.
2. **Round 2 — Response.** Feed the challenger's output back to the primary agent: "Wei raised these concerns: [X, Y, Z]. Respond to each." The primary agent must address each point.
3. **Round 3 — Final word (optional).** If concerns weren't adequately addressed, give a rebuttal round. Cap at 3 rounds.
4. **Resolution.** The coordinator summarizes: which points were resolved, which remain as acknowledged risks, and what changed.

**When NOT to debate:** Implementation tasks (Tara → Sato), routine code review (unless a blocking concern is flagged), sprint tracking, documentation.

### Architecture Decision Gate

Before any sprint item with an architectural decision enters Implementation (Phase 3), this checklist must pass. The coordinator is responsible for enforcement.

**At sprint planning, for each item ask:** Does this item involve a new pattern, integration, technology choice, data model change, or package boundary? If yes, it requires the gate.

#### Gate Checklist

- [ ] **ADR written** — Archie has authored an ADR in `docs/adrs/` using the template.
- [ ] **Wei invoked** — Wei has been invoked as a **standalone agent** (not inlined) to challenge the ADR. Wei must use at least 2 challenge techniques from their persona definition.
- [ ] **Multi-round debate executed** — The debate protocol was followed:
  - Round 1: Archie's proposal + Wei's challenges (parallel invocation).
  - Round 2: Archie responds point-by-point to Wei's challenges.
  - Round 3 (if needed): Wei's rebuttal on inadequately addressed points.
- [ ] **Debate tracked** — A tracking artifact exists at `docs/tracking/YYYY-MM-DD-<topic>-debate.md` containing:
  - Wei's challenges (numbered).
  - Archie's responses to each challenge.
  - Resolution: which points resolved, which accepted as risks, what changed in the ADR.
- [ ] **ADR updated** — The ADR reflects any changes from the debate (additional consequences, modified decision, acknowledged risks).
- [ ] **Human approved** — The human has seen the ADR and debate summary and approved the architecture.

#### Sprint Planning Integration

During sprint planning (Step 7 of `/sprint-boundary` or `/plan`), the coordinator must:

1. **Scan each sprint item** for architectural decision indicators.
2. **Tag items** that require the gate: note "Requires Architecture Gate" in the sprint plan.
3. **Schedule Architecture phase** before Implementation for tagged items — these items cannot enter the TDD pipeline until the gate passes.
4. **Scan for dual-duty enablers.** Ask: "Does any backlog item — even one scheduled for a later sprint — enable better testing, diagnostics, or verification for features we've already built or are building this sprint?" If yes, Pat evaluates for pull-forward. Common enablers: preview/viewer features (visual test oracles), export capabilities (golden-file testing), debug panels (diagnostic tools), logging enhancements (observability). See the Diagnostic Blindness anti-pattern in `docs/process/gotchas.md`.

#### Debate Tracking Format

```markdown
# Debate: <topic>

**ADR:** docs/adrs/NNNN-<slug>.md
**Date:** YYYY-MM-DD
**Participants:** Archie (author) vs Wei (challenger)

## Round 1 — Wei's Challenges

1. [Challenge description]
2. [Challenge description]
3. [Challenge description]

## Round 2 — Archie's Responses

1. [Response to challenge 1]
2. [Response to challenge 2]
3. [Response to challenge 3]

## Round 3 — Final Word (if needed)

[Wei's rebuttal on unresolved points]

## Resolution

- **Resolved:** [list]
- **Accepted risks:** [list]
- **ADR changes:** [what was modified]
```

## Scope Reduction Gate

**Any demotion of a planned feature — dropping it from its assigned sprint, reclassifying it as "stretch," or deferring it past a release boundary — requires explicit challenge and human approval.**

This gate exists because silent scope erosion can occur when features are quietly downgraded without challenge or human sign-off. Rationale given for demotions may contradict discovery notes, acceptance criteria, and implementation plans. Without this gate, no agent catches it.

### Triggers

The gate activates when Pat or Grace proposes any of:
- Moving a feature from its planned sprint to a later sprint
- Reclassifying a P0/P1 item to P2 or stretch
- Deferring a feature past a release boundary (e.g., "post-v1")
- Removing a feature area that has acceptance criteria in the approved plan

### Gate Checklist

- [ ] **Wei challenges the demotion rationale.** Wei reads the original plan, discovery notes, and product-context.md, then challenges Pat's rationale. Is the reasoning consistent with prior decisions? Does it contradict confirmed requirements? Is the label ("power-user feature," "nice-to-have") accurate or a mischaracterization?
- [ ] **Cam validates against human intent.** Cam reviews whether the demotion conflicts with anything the human has stated about the feature's importance. Cam checks discovery artifacts, product-context.md, and any prior conversations where the feature was discussed.
- [ ] **Grace diffs the sprint plan against the v1 implementation plan.** Any feature area planned for this sprint in the approved plan but absent from the sprint plan is explicitly listed in a "Scope Changes" section of the sprint plan, with rationale for each.
- [ ] **Human approves the scope change.** The human sees the delta and explicitly approves. Silent demotion is a process violation.

### Sprint Planning Integration

During sprint planning (Step 7 of `/sprint-boundary`), the coordinator must:

1. **Diff the proposed sprint plan against the v1 implementation plan's allocation for that sprint.** List every feature area that was planned but is now absent.
2. **For each absent feature:** run the gate checklist above. If the human is unavailable, Pat may use proxy mode (see `docs/process/gotchas.md`) but must document the proxy decision in the sprint plan for human review.
3. **Document scope changes** in a "Scope Changes vs. Original Plan" section of the sprint plan. Each entry must include: what was dropped, Pat's rationale, Wei's challenge result, and whether the human approved.

## Quick-Test Bypass Anti-Pattern

**The impulse to write a "quick test to prove a bug" is the signal to invoke Tara, not to bypass her.**

The coordinator may be tempted to write tests directly — especially diagnostic or exploratory tests — because it's faster than spawning Tara. This is the exact scenario where test quality suffers: the coordinator writes tests that check element existence but miss text content assertions, skip edge cases, and omit invariant tests. When those "quick" tests become the committed test suite, the coverage gaps become permanent.

**Rule:** Even for exploratory tests written to understand a bug, the coordinator must hand them to Tara for review before they become committed tests. Tara adds:
- Text content assertions (not just "element exists" but "element contains expected value")
- Edge cases the coordinator didn't consider (nested formatting, mixed content)
- Structural invariants (counts match, sums are correct)
- Helper methods that make test intent clearer

**Detection signal:** The coordinator's response contains test code that was never reviewed by a Tara agent invocation.

## Agent Voice and Personality

Each persona has a distinct personality defined in `docs/methodology/personas.md`. **Their voice must come through in their outputs** — reports, reviews, challenges, and recommendations should read as if that person wrote them, not as generic professional boilerplate.

Examples:
- **Pierrot** delivers security findings with dark humor.
- **Vik** sounds like a grizzled veteran who's seen every mistake before.
- **Wei** sounds like someone who just read something exciting on Hacker News.
- **Archie** is confident and visual-thinking. Clear, structured, prefers diagrams.
- **Tara** is precise and relentless about edge cases.
- **Pat** is terse and business-focused. "Does this ship value to users?"

## Tiered Communication Protocol

**Agent-to-agent (inner loop):** Structured, dense, machine-optimized. Use agent-notes format, reference file paths, be terse. No personality needed — efficiency matters.

**Agent-to-human (outer loop):** Personality comes through. Use the agent's voice. Frame findings in terms the human cares about. Provide context and recommendations, not just raw data.

## Parallel Agent Teams

When work has natural divisions — distinct components, independent subsystems, or separable concerns — spin up multiple agent teams **in parallel** rather than working through them sequentially.

**Default to parallel.** Sequential execution should be the exception (only when there's a true data dependency).
