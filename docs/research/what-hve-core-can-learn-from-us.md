---
agent-notes: { ctx: "vteam-hybrid strengths HVE Core lacks", deps: [docs/research/what-we-learn-from-hve-core.md, docs/methodology/personas.md, docs/process/team-governance.md], state: active, last: "coordinator@2026-03-02" }
---

# What HVE Core Can Learn from Us

> **Source:** Comparison of [microsoft/hve-core](https://github.com/microsoft/hve-core) (35 agents, Copilot) vs vteam-hybrid (18 agents, Claude Code)
> **Reviewed:** 2026-03-02
> **Companion doc:** `docs/research/what-we-learn-from-hve-core.md`

This doc captures areas where vteam-hybrid's agent system is stronger, more nuanced, or covers ground that HVE Core doesn't address. These are patterns worth preserving and strengthening.

## High-Impact Strengths

### 1. Adversarial Debate as a First-Class Protocol

**What we do:** Wei exists as a dedicated devil's advocate persona with a defined debate protocol — multi-round (opening → response → rebuttal → resolution), mandatory for ADR review, security audits, pre-release gates, and architecture disagreements. The Architecture Gate requires Wei to challenge Archie as a standalone agent before any ADR is accepted.

**What HVE does:** Architecture review is a single `system-architecture-reviewer` agent that produces findings. There is no adversarial counterpart, no structured debate, and no requirement that decisions be challenged before acceptance.

**Why it matters:** Consensus without challenge produces blind spots. Wei's role isn't to be right — it's to ensure the team has considered the uncomfortable alternatives. HVE's architecture review is thorough but unchallenged, which means groupthink can survive the review process intact.

### 2. Triple-Lens Code Review

**What we do:** Code review invokes three independent agents in parallel, each with a distinct lens:
- **Vik** — Simplicity, maintainability, dead code, pattern enforcement
- **Tara** — Test coverage, test quality, missing edge cases
- **Pierrot** — Security vulnerabilities, compliance, license audit

Each lens has independent veto power. Findings are synthesized but perspectives are never merged — disagreements between reviewers are surfaced, not smoothed over.

**What HVE does:** A single `pr-review` agent evaluates 8 dimensions (functional correctness, design, security, testing, performance, documentation, error handling, style). One agent, one pass, one perspective.

**Why it matters:** A single reviewer optimizes for consistency but misses what a specialist would catch. Vik notices a premature abstraction that a generalist wouldn't flag. Pierrot spots a timing attack that a non-security reviewer would miss. Tara catches an untested error path that looks fine to everyone else. Parallel independent lenses beat a single comprehensive checklist.

### 3. Explicit Veto Power with Escalation Chains

**What we do:** Two agents have formal veto power:
- **Tara** can block merges on test coverage grounds
- **Pierrot** can block merges or releases on security or compliance grounds

Vetoes must be documented with rationale. Escalation path: veto → Pat (product scope) or Grace (sprint scope) → human as final arbiter. Grace can override Pat's prioritization for tech debt open 3+ sprints.

**What HVE does:** Agents produce findings with severity levels, but no agent can formally block progress. There are no veto mechanics, no escalation chains, and no override authorities.

**Why it matters:** Without veto power, review findings become suggestions. A team under deadline pressure will acknowledge a security finding and ship anyway. Veto power with escalation ensures that critical findings require an explicit decision to override — the human must consciously accept the risk rather than passively ignoring it.

### 4. Phase-Dependent Team Composition

**What we do:** The coordinator selects different team structures for each of 7 phases. Discovery gets Cam + Pat + Dani + Wei + User Chorus. Architecture gets Archie + Wei + Vik + Pierrot + Ines. Implementation gets Tara → Sato. Code Review gets Vik + Tara + Pierrot. Each phase has a named lead and a defined collaboration model (blackboard, ensemble, pipeline, market).

**What HVE does:** Agents are invoked individually by the user. The RPI workflow defines a sequence (Research → Plan → Implement → Review) but doesn't prescribe which agents collaborate within each phase or how they interact. Team composition is ad hoc.

**Why it matters:** Knowing *who* works together and *how* they interact for each type of work eliminates coordination overhead. The user doesn't have to think about which agents to invoke — the phase determines the team. This is especially valuable for less experienced users who wouldn't know to invoke Wei during architecture review.

### 5. Sprint and Program Management

**What we do:** Grace manages sprint tracking, velocity, work distribution, ceremonies, and cross-team coordination. Pat manages the backlog, priorities, acceptance criteria, and acts as human proxy when the user is unavailable. Together they provide full program management from backlog grooming through sprint execution to retrospectives.

**What HVE does:** `github-backlog-manager` creates and manages GitHub issues. `ado-prd-to-wit` converts PRDs to Azure DevOps work items. These are utilities, not management agents — they don't track velocity, run ceremonies, manage priorities, or coordinate across work streams.

**Why it matters:** HVE is excellent at individual task execution but doesn't manage the work *around* tasks — prioritization, sprint planning, capacity management, or retrospectives. For sustained multi-sprint projects, this gap means the human carries all coordination overhead.

### 6. Human Proxy Mode

**What we do:** When the human declares unavailability, Pat answers product questions using `docs/product-context.md` as a guide, with explicit guardrails: Pat cannot approve ADRs, change scope, make architectural choices, merge, or override security/test vetoes. All decisions are logged in `.claude/handoff.md` for human review on return.

**What HVE does:** No equivalent. When the human is away, work stops or proceeds without product guidance.

**Why it matters:** Real-world development has gaps — the human steps out, is in meetings, or hands off a session overnight. Proxy mode lets the team continue making product-level micro-decisions (acceptance criteria interpretation, priority calls between similar items) without blocking on the human for every question, while maintaining guardrails that prevent unauthorized scope changes.

### 7. Cam's Elicitation-First Pattern

**What we do:** Cam is a dedicated human interface agent whose entire purpose is to probe, clarify, and pressure-test before any work begins. Cam's workflow is structured: Orient → Prioritize → Probe → Translate → Actionize. The "Don't Run With Vague Input" rule is a system-level constraint that routes all unclear requests through Cam.

**What HVE does:** No equivalent elicitation agent. The user writes a task description and invokes an RPI agent directly. If the description is vague, the researcher will investigate but won't push back on the user to clarify intent.

**Why it matters:** The most expensive mistake in software is building the wrong thing. Cam's job is to catch this before any technical work begins. HVE's Research phase investigates *how* to solve a problem, but doesn't question *whether it's the right problem*. The elicitation step is upstream of research.

## Medium-Impact Strengths

### 8. User Chorus for Usability Feedback

We have a multi-archetype user panel (Alex the power user, Jordan the impatient novice, Sam the accessibility-dependent user, Riley the non-technical stakeholder, Morgan the mobile-first user) that provides simulated usability feedback during design phases. HVE has no equivalent. Their Design Thinking agents coach methodology but don't simulate end-user perspectives.

### 9. Agent Voice as a Quality Signal

Our agents have distinct, documented personalities — Pierrot's dark humor, Vik's grizzled veteran voice, Wei's provocative challenges, Pat's terse business focus. These aren't cosmetic. Voice distinctiveness makes it immediately obvious which agent produced which output, prevents agents from blurring into generic "assistant" tone, and makes it easier for the human to weigh perspectives ("that sounds like a Pierrot concern, not a Vik concern").

HVE agents are professional and consistent but lack distinctive voice. Their outputs are interchangeable in tone.

### 10. Done Gate as Explicit Checklist

Our 15-item Done Gate is a formal checklist that every work item must pass before closing. It covers code, tests, docs, security, accessibility, and tracking. HVE's review phase validates against research and plan specs, but doesn't have an explicit, enumerated gate that applies uniformly to all work items.

### 11. Tech Debt Escalation with Override Authority

Grace can override Pat's prioritization for tech debt that has been open 3+ sprints — it automatically escalates to P0. This prevents the common pattern where tech debt is perpetually deprioritized in favor of features. HVE has no equivalent mechanism; tech debt management is left to the human.

### 12. Document Ownership Model

Each doc in our system has a named agent owner with defined update triggers. Archie owns ADRs. Tara owns test strategy. Pierrot owns SBOM and threat model. Diego owns changelogs. This prevents docs from going stale because there's always an accountable party. HVE has community maintainers for the framework itself but no per-doc ownership within a project.

## Structural Differences Worth Noting

### Agent Count: Quality over Quantity

HVE has 35 agents to our 18, but many of HVE's agents are platform-specific utilities (ADO integration, GitHub backlog management, Copilot installer) or subagent support roles (researcher-subagent, phase-implementor, plan-validator). Our smaller roster has broader per-agent scope and avoids the coordination overhead of 35 specialized agents.

| Category | HVE | vteam-hybrid |
|----------|-----|-------------|
| Core workflow | 5 (RPI chain) | 5 (Cam, Sato, Tara, Pat, Grace) |
| Architecture & design | 3 | 3 (Archie, Dani, Wei) |
| Review & security | 2 | 3 (Vik, Tara, Pierrot) |
| Infrastructure & ops | 0 | 1 (Ines) |
| Data science | 3 | 1 (Debra) |
| Cloud specialists | 0 | 3 (adaptive to AWS/Azure/GCP) |
| Platform utilities | 6 (GitHub, ADO, installer) | 0 (commands instead) |
| Subagent support roles | 8 | 0 |
| Documentation | 0 | 1 (Diego) |
| User simulation | 0 | 1 (User Chorus) |
| Design methodology | 2 (DT coaches) | 0 (Dani covers informally) |
| Prompt engineering | 2 | 0 |

### Commands vs Agents

Where HVE creates agents for utility tasks (installing plugins, managing backlogs, creating PRs), we use slash commands (`/kickoff`, `/sprint-boundary`, `/handoff`, `/resume`). Commands are lighter weight, don't require persona definitions, and are easier to maintain. The tradeoff is that agents can maintain state across interactions while commands are stateless.

### Adaptive Cloud Specialists

Our three cloud agents (Cloud Architect, Cloud CostGuard, Cloud NetDiag) each adapt to AWS, Azure, or GCP based on context. HVE has no cloud-specific agents — their platform focus is Azure DevOps and GitHub, not cloud infrastructure.

## Summary

Our system's core advantages are in **governance** (veto power, escalation, debate protocol), **human interface** (Cam's elicitation, proxy mode, user chorus), and **program management** (sprint lifecycle, tech debt escalation, document ownership). HVE's core advantages are in **execution rigor** (evidence tracing, constraint-based design, phase separation) and **platform integration** (Copilot, ADO, GitHub).

The two systems are complementary rather than competitive. Our governance and human-interface patterns would strengthen HVE's execution model. Their evidence-tracing and constraint patterns would strengthen our architecture and implementation phases.
