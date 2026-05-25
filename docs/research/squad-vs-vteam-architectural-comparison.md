---
agent-notes:
  ctx: "architectural comparison of Squad vs vteam-hybrid agent systems"
  deps: [docs/methodology/personas.md, docs/methodology/phases.md, docs/process/team-governance.md, docs/research/what-we-learn-from-hve-core.md]
  state: active
  last: "archie@2026-03-21"
  key: ["Squad = npm CLI + Copilot runtime, vteam = GitHub template + Claude Code runtime", "three-layer memory vs ADR+gotchas", "explicit coordinator vs implicit CLAUDE.md rules"]
---

# Squad vs. vteam-hybrid: Architectural Comparison

> **Source:** [bradygaster/squad](https://github.com/bradygaster/squad) (npm CLI, GitHub Copilot runtime) vs vteam-hybrid (GitHub repo template, Claude Code runtime)
> **Reviewed:** 2026-03-21
> **Author:** Archie (architecture lens)
> **Companion docs:** `what-we-learn-from-hve-core.md`, `what-hve-core-can-learn-from-us.md`

## Executive Summary

Squad and vteam-hybrid solve the same problem -- multi-agent AI team coordination -- but from opposite architectural starting points. Squad is a **runtime**: an npm package that generates and manages agent state through CLI commands, with GitHub Copilot as the AI backend. vteam-hybrid is a **template**: a static file structure that configures Claude Code's built-in orchestration through CLAUDE.md rules and subagent definitions. The structural differences follow directly from this distinction.

Neither system is strictly superior. Squad excels at **approachability, knowledge accumulation, and runtime tooling**. vteam-hybrid excels at **governance, process rigor, and team composition dynamics**. The most impactful improvements we could make would borrow Squad's knowledge layering without importing its runtime dependency.

---

## 1. Structural Patterns Squad Does Better

### 1.1 Three-Layer Knowledge Architecture

Squad's most compelling structural advantage is its layered memory system:

```
Layer 1: Skills       (.squad/skills/{name}/SKILL.md)     -- portable, reusable, team-wide
Layer 2: Decisions    (.squad/decisions.md)                -- team policy, every agent reads
Layer 3: History      (.squad/agents/{name}/history.md)    -- personal, per-agent, accumulated
```

Each layer serves a different temporal scope:
- **Skills** are permanent, transferable patterns that survive project changes (e.g., "how to set up CI with GitHub Actions").
- **Decisions** are project-scoped policies that every agent reads before working (e.g., "use PostgreSQL, no Friday deploys").
- **History** is personal context that compounds per-agent (e.g., "the auth module uses JWT with refresh tokens in src/auth/").

**What we have instead:** ADRs (architecture decisions), `docs/process/gotchas.md` (agent-owned sections for patterns/anti-patterns), and Claude Code's built-in MEMORY.md. The information is there but lacks Squad's clean separation. Our gotchas.md mixes what Squad would split across skills and decisions. Our ADRs are more rigorous than Squad's decisions (they require debate and approval), but they also have higher friction -- you don't write an ADR for "always use single quotes."

**Assessment:** Squad's approach compounds faster for everyday conventions. A user saying "always use Prettier with tabs" creates a directive that every agent reads permanently. In our system, that same preference either goes into CLAUDE.md (high-friction, pollutes the root doc), gotchas.md (wrong semantic bucket), or gets lost between sessions.

### 1.2 The Scribe Pattern (Silent Background Knowledge Worker)

Squad's Scribe is architecturally elegant: a background agent that silently merges decisions, deduplicates the shared brain, propagates cross-agent updates, and logs sessions. The user never interacts with the Scribe directly.

```
Agent A writes: .squad/decisions/inbox/keaton-api-versioning.md
Agent B writes: .squad/decisions/inbox/fenster-error-handling.md
                            |
                     Scribe merges
                            |
                     .squad/decisions.md (canonical, deduplicated)
```

The inbox pattern solves a real problem: parallel agents making overlapping decisions without conflict. Write to your inbox file, the Scribe consolidates. This is append-only, merge-safe, and handles git worktree divergence gracefully via `merge=union`.

**What we have instead:** No equivalent. ADRs are atomic documents that don't conflict because they have sequential numbers, but they only capture big decisions. Small team conventions fall through the cracks between sessions. Our `/handoff` command captures session state but doesn't merge knowledge across agent boundaries.

**Assessment:** The Scribe solves a problem we currently handle manually or lose to context window resets. A background knowledge merger would improve session continuity significantly.

### 1.3 Explicit Coordinator as Routing Engine

Squad's coordinator is a defined entity with explicit routing rules:

```
.squad/routing.md:
  core-runtime     -> @fenster
  prompt-architecture -> @verbal
  type-system      -> @edie
  security         -> @baer
```

This is a lookup table. Work arrives, the coordinator pattern-matches against routing rules, and dispatches to the right agent. The routing is inspectable (read the file), editable (change the file), and auditable (orchestration-log records every dispatch with rationale).

**What we have instead:** Persona triggers embedded in `docs/process/team-governance.md` as a human-readable table, plus phase-selection logic in `docs/methodology/phases.md` as a Mermaid flowchart. The coordinator behavior is implicit -- Claude Code reads CLAUDE.md and makes routing decisions based on instruction-following, not a structured lookup.

**Assessment:** Squad's approach is more debuggable. When routing goes wrong, you read `routing.md` and the `orchestration-log/` to see exactly why Agent X got the work. In our system, routing is emergent from Claude Code's interpretation of our governance docs, which is harder to audit. The trade-off is that our phase-based composition is richer -- we don't just route to a single agent, we assemble a team with defined interaction patterns (blackboard, ensemble, pipeline). Squad routes to individuals; we compose teams.

### 1.4 SDK-First Configuration (`squad.config.ts`)

Squad's builder-function approach (`defineSquad`, `defineAgent`, `defineRouting`) provides:
- Type safety and editor autocomplete
- Runtime validation with clear error messages
- Single source of truth (TypeScript) that generates governance markdown
- CI-checkable drift detection (`squad build --check`)

```typescript
export default defineSquad({
  team: defineTeam({ name: 'Core', members: ['@edie'] }),
  agents: [
    defineAgent({ name: 'edie', role: 'TS Engineer', model: 'claude-sonnet-4' }),
  ],
  routing: defineRouting({ rules: [...], fallback: 'coordinator' }),
});
```

**What we have instead:** Hand-authored markdown agent definitions in `.claude/agents/*.md` with YAML frontmatter. No build step, no validation, no drift detection.

**Assessment:** The SDK approach is more robust for teams that modify agent definitions frequently. Our markdown-first approach is simpler for template consumers who just want to start using the system without a build step. For a template project, markdown-first is the right default. But we should consider schema validation for agent-notes (item 10 from the HVE comparison).

### 1.5 Orchestration Logging

Squad logs every agent spawn to `.squad/orchestration-log/{timestamp}-{agent-name}.md` with structured fields: who was routed, why, what mode, what files, what outcome. This is append-only and never edited.

**What we have instead:** Debate tracking in `docs/tracking/` for architecture decisions. No equivalent for routine agent invocations. We know Archie debated Wei on an ADR; we don't know which agents were invoked for a code review last session.

**Assessment:** Orchestration logging provides auditability we currently lack. Low-cost addition that would improve session resumption and retrospectives.

---

## 2. Patterns vteam-hybrid Does Better

### 2.1 Phase-Dependent Team Composition

This is our most significant structural advantage. Squad routes work to individuals; we compose teams with defined interaction models:

| Phase | Team | Interaction Model |
|-------|------|------------------|
| Discovery | Cam + Pat + Dani + Wei + User Chorus | Blackboard (open brainstorm) |
| Architecture | Archie + Wei + Vik + Pierrot + Ines | Ensemble + adversarial debate |
| Implementation | Tara then Sato | Pipeline (strict sequential) |
| Code Review | Vik + Tara + Pierrot (+ Archie, Dani) | Parallel independent lenses |
| Debugging | Sato + Tara + Vik + Pierrot | Blackboard (shared investigation) |

Squad's coordinator spawns agents for a task but doesn't define how they interact. If you say "team, build X," the coordinator fans out to multiple agents in parallel, collects results, and synthesizes. There is no concept of a blackboard vs. pipeline vs. ensemble -- it is always fan-out/collect.

**Why this matters:** Different work types genuinely need different collaboration patterns. Architecture decisions need adversarial challenge (Wei vs. Archie). Implementation needs strict handoffs (Tara writes tests, Sato implements). Code review needs independent parallel lenses. A single fan-out/collect model cannot express these distinctions.

### 2.2 Formal Governance (Vetoes, Gates, Escalation)

Our governance machinery has no Squad equivalent:

- **Veto power:** Tara (test coverage) and Pierrot (security/compliance) can formally block progress, with documented escalation paths to Pat, Grace, and ultimately the human.
- **Architecture Gate:** ADRs require Wei's adversarial challenge as a standalone agent, multi-round debate, debate tracking, and human approval before implementation begins.
- **Done Gate:** 15-item checklist (tests, types, lint, format, code review, acceptance criteria, docs, accessibility, board status, migration safety, API compat, tech debt, SBOM, operational baseline, integration smoke test).
- **Scope Reduction Gate:** Any feature demotion requires Wei challenge, Cam validation against human intent, Grace plan diff, and human approval.

Squad has reviewer gates (an agent's work can be reviewed before acceptance) and ceremonies (design review, retrospective), but these are lighter-weight. There are no formal vetoes, no escalation chains, no multi-round debate protocols.

**Why this matters:** Governance prevents silent quality erosion. Without formal vetoes, security findings become suggestions. Without the Architecture Gate, decisions go unchallenged. Without the Scope Reduction Gate, features get quietly dropped. Squad optimizes for throughput; we optimize for correctness under pressure.

### 2.3 Adversarial Debate as a First-Class Protocol

Our debate protocol is structural, not optional:

1. Archie proposes (ADR).
2. Wei challenges (standalone agent, minimum 2 techniques).
3. Archie responds point-by-point.
4. Optional rebuttal round.
5. Resolution documented in tracking artifact.
6. ADR updated with debate outcomes.

Squad has no adversarial agent. The closest equivalent is the `waingro` role ("Adversarial testing, edge cases, regression scenarios") but this is adversarial about *code*, not about *decisions*. No Squad agent exists to challenge architectural choices.

### 2.4 Anti-Pattern Catalog with Detection Signals

Our `docs/process/gotchas.md` catalogs named anti-patterns with explicit detection signals and fixes:

- **Plan-as-Bypass** (detection: coordinator's first tool call is `Read` on a source file, not governance docs)
- **Quick-Test Bypass** (detection: test code in coordinator response with no Tara agent invocation)
- **Solo-Coordinator** (detection: human asked for a persona but no Task tool calls appear)
- **Diagnostic Blindness** (detection: Tara proposes heavyweight test infra while a preview feature sits in the backlog)
- **Horizontal Blindness** (detection: 3+ sprints with no logging, broken README)
- **Green-Bar-Red-Product** (detection: all items pass Done Gate but product is not shippable)

Squad's skills system captures patterns and anti-patterns, but they are organic (learned from work) rather than structural (baked into governance). Our anti-patterns are not just documentation -- they have detection signals that the coordinator actively monitors.

### 2.5 Document Ownership Model

Every document in our system has a named agent owner with defined update triggers:

| Doc | Owner | Update Trigger |
|-----|-------|---------------|
| ADRs | Archie | Architectural decisions |
| Threat model | Pierrot | New endpoints, data types, auth flows |
| Test strategy | Tara | New test patterns or coverage targets |
| SBOM | Pierrot | Dependency add/remove/upgrade |
| Changelog | Diego | Releases |
| Tech debt | Grace (track) / Pat (prioritize) | Sprint boundaries |

Squad's Scribe owns the decision log and session logs, but other documents have no assigned ownership. There is no mechanism to ensure the README stays current or the deployment docs update when infrastructure changes.

### 2.6 Human Proxy Mode

When the human is unavailable, Pat answers product questions within explicit guardrails. Pat can prioritize backlog items, accept features against existing criteria, defer items. Pat cannot approve ADRs, change scope, make architectural choices, merge, or override vetoes. All proxy decisions are logged for human review.

Squad has no equivalent. When the human is away, work continues without product guidance or blocks entirely.

---

## 3. The Coordinator Pattern: Explicit vs. Implicit

### Squad's Explicit Coordinator

Squad has a named coordinator entity that:
- Reads routing rules from `.squad/routing.md`
- Decomposes multi-part tasks into parallel work units
- Pattern-matches work types to agents
- Manages background vs. sync execution
- Logs every dispatch to orchestration-log
- Enforces reviewer gates
- Manages model selection per agent/task
- Detects circular dependencies between agents

The coordinator does not do domain work. It routes, dispatches, and synthesizes.

### vteam-hybrid's Implicit Coordinator

We have no named coordinator entity. Claude Code itself acts as the coordinator by:
- Reading CLAUDE.md, which references governance docs
- Following persona trigger rules from `team-governance.md`
- Following phase selection logic from `phases.md`
- Spawning subagents via the Task tool when triggered
- Composing teams based on the current phase

### Trade-Off Analysis

| Criterion | Squad (explicit) | vteam-hybrid (implicit) |
|-----------|-----------------|------------------------|
| **Debuggability** | High -- read routing.md and orchestration-log | Low -- routing is emergent from instruction-following |
| **Flexibility** | Moderate -- routing rules are pattern-based | High -- the coordinator can reason about novel situations |
| **Team composition** | Single-agent routing | Multi-agent team assembly with interaction models |
| **Auditability** | High -- every dispatch logged with rationale | Low -- no structured dispatch log |
| **Failure modes** | Misroute (wrong agent gets work) | Mis-composition (wrong team assembled) or process skip |
| **User control** | Edit routing.md or name an agent directly | Edit CLAUDE.md or invoke a persona directly |
| **Runtime dependency** | Requires Squad CLI installed | No dependency -- CLAUDE.md is read natively |

**Verdict:** These are genuinely different architectures with different strengths. Squad's explicitness is better for debugging and auditing. Our implicitness is better for flexible team composition and handling novel situations. The gap in auditability is worth closing -- we could add dispatch logging without changing our coordinator model.

---

## 4. Knowledge Accumulation: Which Compounds Better?

### Squad's Approach

```
Session 1: Agent learns auth uses JWT -> history.md
Session 2: Agent reads history.md, knows JWT without re-discovering
Session 3: Team decides "always use JWT" -> decisions.md
Session 5: Pattern distilled into skill -> skills/jwt-auth/SKILL.md
```

Knowledge flows bottom-up: personal observation -> team decision -> portable skill. The compounding is organic. Skills are the highest-value artifact because they survive project changes and can be ported to new repos.

**Strengths:**
- Low friction -- agents write knowledge as they work
- Layered -- personal, team, and portable knowledge are distinct
- Auto-compacted -- history summarizes at ~12KB, decisions archive when stale
- Directive capture -- "always..." and "never..." statements become permanent team rules

**Weaknesses:**
- No adversarial challenge on decisions -- if an agent writes a bad decision, it persists until someone notices
- No formal approval process -- decisions accumulate without human sign-off
- Quality varies -- organic knowledge ranges from "JWT uses refresh tokens" (useful) to "I renamed a file" (noise)
- Scribe deduplication is heuristic -- overlapping decisions may consolidate incorrectly

### vteam-hybrid's Approach

```
Sprint 1: Archie writes ADR -> docs/adrs/0001-*.md (debated, approved)
Sprint 1: Sato discovers gotcha -> docs/process/gotchas.md (agent-owned section)
Sprint 2: Tara discovers test pattern -> docs/process/gotchas.md (testing section)
Sprint 3: Retro identifies anti-pattern -> named, given detection signal
Sprint N: Agent-notes provide per-file context bootstrapping
```

Knowledge flows through formal processes: discovery -> documentation -> governance integration. The compounding is deliberate.

**Strengths:**
- High quality -- ADRs are debated, challenged, and approved
- Named anti-patterns with detection signals are actionable, not just informational
- Document ownership ensures maintenance
- Agent-notes provide per-file context without reading the full file

**Weaknesses:**
- High friction -- writing an ADR for "use single quotes" is overkill
- No equivalent to Squad's directives for quick preference capture
- Session-to-session continuity relies on MEMORY.md (Claude Code feature) and `/handoff` (manual process)
- No portable skills concept -- knowledge is project-bound

### Verdict

**Squad compounds faster for everyday knowledge. vteam-hybrid compounds better for architectural knowledge.**

Squad wins on low-friction convention capture: the directive system ("always X", "never Y") requires zero process overhead and permanently shapes agent behavior. This is the knowledge that matters most for day-to-day coding consistency.

vteam-hybrid wins on high-stakes decision quality: the ADR + debate + gate pipeline produces well-reasoned, challenged, documented decisions. This is the knowledge that matters most for architectural integrity.

The ideal system has both: low-friction capture for conventions, high-rigor processes for architecture. We are missing the low-friction layer.

---

## 5. The Casting System: Names and Identity

### Squad's Approach: Themed Fictional Names

Squad draws agent names from fictional universes: The Usual Suspects (Keaton, Verbal, Fenster, Hockney, McManus), Breaking Bad, Star Wars, Firefly, etc. The `casting/` directory manages name allocation with policies and registries.

**Effects:**
- **Personality by association.** Keaton (lead) evokes "the one who sees the whole board." Verbal (prompt engineer) evokes the unreliable narrator who crafts stories. The names carry connotative weight from their source material.
- **Engagement.** It is more fun to say "have Keaton review the architecture" than "have Agent-7 review the architecture."
- **Themed consistency.** A team drawn from one universe feels like a cohesive group, not a random collection.
- **Scaling.** The casting system handles team growth -- when you need a new agent, you draw the next name from the universe, preserving thematic consistency.

**Costs:**
- **Cultural specificity.** Not everyone has seen The Usual Suspects. The name "Keaton" carries no meaning if you don't know the film.
- **Role opacity.** "Keaton" does not tell you what Keaton does. You must read the charter. "Verbal" is the prompt engineer -- but only if you know the film.
- **Onboarding friction.** A new team member must learn both the role system and the naming system.

### vteam-hybrid's Approach: Descriptive Names with Personality

Our agents use descriptive names with embedded personality:
- **Archie** (architecture) -- confident, visual-thinking, prefers diagrams
- **Sato** (SDE) -- the workhorse, strong opinions held loosely
- **Tara** (tester) -- precise, relentless about edge cases
- **Pierrot** (security) -- dark humor, finds vulnerabilities
- **Wei** (devil's advocate) -- reads Hacker News, challenges everything
- **Vik** (veteran reviewer) -- grizzled, seen every mistake

**Effects:**
- **Role discoverability.** "Archie" + "architecture" is more transparent than "Keaton" + "Lead."
- **Personality in voice.** Each agent has documented voice characteristics that come through in outputs.
- **Lower onboarding friction.** Names are suggestive of roles without requiring cultural context.

**Costs:**
- **Less thematic cohesion.** The names don't come from a shared universe. The team feels like a collection of individuals, not a themed ensemble.
- **Less engagement.** The names are functional, not playful. "Invoke Archie" is less engaging than "invoke Keaton."

### Verdict

This is a genuine trade-off between **discoverability** and **engagement**.

Squad's approach is more fun and creates stronger team identity. The fictional universe creates a shared reference frame that makes the team feel cohesive. But it requires cultural literacy and obscures roles.

Our approach is more transparent and accessible. You can guess what Tara does (testing) without reading her charter. But the names are less memorable and the team feels less like a team.

For a **template project** used by many different people, discoverability wins over engagement. Our naming approach is the right default. But the personality dimension -- giving agents distinct voice and opinions -- is something both systems share and both do well.

---

## 6. Highest-Impact Changes for Approachability Without Losing Strengths

### 6.1 Add a Lightweight Directives Layer (High Impact, Low Effort)

**Borrow:** Squad's directive capture system.
**Adapt:** Add a `docs/team-directives.md` file (owned by the coordinator) where quick conventions are captured. Not ADR-weight -- just "always X" / "never Y" statements that every agent reads.

**Implementation:**
- Add `docs/team-directives.md` with append-only convention entries.
- Add a rule to CLAUDE.md: "When the human says 'always', 'never', 'from now on', or 'remember to', append to `docs/team-directives.md`."
- All agent definitions include `docs/team-directives.md` in their deps.
- The Scope Reduction Gate does not apply to directives (they are lightweight by design).

**What we keep:** ADRs for architectural decisions. The directive layer handles the space below ADR-threshold.

**Risk:** Directive accumulation without review. Mitigate by having Grace scan directives at sprint boundaries for conflicts or staleness.

### 6.2 Add Per-Agent Knowledge Files (High Impact, Medium Effort)

**Borrow:** Squad's per-agent `history.md` pattern.
**Adapt:** Add `.claude/knowledge/{agent-name}.md` files where agents append project-specific learnings after completing work. Different from gotchas.md (which is cross-cutting) -- these are domain-specific context that helps the agent resume faster.

**Implementation:**
- Create `.claude/knowledge/` directory.
- Each agent appends discoveries after significant work (not every invocation -- only when something novel is learned).
- Progressive summarization at ~8KB (smaller than Squad's 12KB threshold since our context windows are used differently).
- Agent definitions reference their own knowledge file.

**What we keep:** Gotchas.md for cross-cutting anti-patterns. Agent-notes for per-file metadata. Knowledge files add the missing per-agent accumulation layer.

**Risk:** Noise accumulation. Mitigate by keeping the append rule strict: "only record project-specific operational knowledge that would save time in a future session."

### 6.3 Add Orchestration Dispatch Logging (Medium Impact, Low Effort)

**Borrow:** Squad's orchestration-log pattern.
**Adapt:** Add `docs/tracking/dispatch-log.md` as an append-only log of agent invocations. Not per-file like Squad (too much overhead) -- a single rolling log.

**Format:**
```markdown
### 2026-03-21T14:30 -- Code Review for #42
- **Invoked:** Vik (simplicity), Tara (coverage), Pierrot (security)
- **Mode:** Parallel
- **Outcome:** 2 Important findings, 0 Critical
```

**What we keep:** Debate tracking for architecture decisions. Dispatch logging adds visibility for routine invocations.

### 6.4 Add a Skills/Recipes Directory (Medium Impact, Medium Effort)

**Borrow:** Squad's skills system.
**Adapt:** Add `docs/skills/` for portable, reusable patterns discovered during work. These are higher-fidelity than directives and lower-ceremony than ADRs.

**Key difference from Squad:** Our skills would be manually curated, not organically grown. Agents propose skills; the human (or a retro) approves promotion. This preserves our quality-over-quantity principle.

**Format:** Use Squad's skill template (context, patterns, examples, anti-patterns) with our agent-notes header.

### 6.5 Do NOT Add: An Explicit Coordinator Entity

Squad's explicit coordinator is architecturally elegant but would be the wrong change for us. Our implicit coordinator (Claude Code + CLAUDE.md) enables flexible team composition that an explicit routing table cannot express. The right fix for our auditability gap is dispatch logging (6.3), not replacing our coordinator model.

### 6.6 Do NOT Add: The Casting System

Themed fictional names are engaging but reduce approachability for a template project with diverse users. Our descriptive names are the right default. If a specific project wants themed names, that is a per-project customization, not a template-level change.

---

## Summary Comparison Table

| Dimension | Squad | vteam-hybrid | Edge |
|-----------|-------|-------------|------|
| Distribution model | npm CLI package | GitHub repo template | Different, not comparable |
| AI runtime | GitHub Copilot | Claude Code | Different, not comparable |
| Knowledge layering | 3-layer (skills/decisions/history) | 2-layer (ADRs + gotchas) | Squad |
| Directive capture | Automatic signal-word detection | Manual (CLAUDE.md or gotchas) | Squad |
| Decision quality | Organic, unreviewed | Debated, gated, approved | vteam-hybrid |
| Team composition | Single-agent routing | Phase-dependent multi-agent teams | vteam-hybrid |
| Interaction models | Fan-out/collect only | Blackboard, pipeline, ensemble, market | vteam-hybrid |
| Governance | Reviewer gates, ceremonies | Vetoes, gates, debate, escalation | vteam-hybrid |
| Adversarial challenge | None (code-level only via waingro) | Wei + Architecture Gate + debate protocol | vteam-hybrid |
| Coordinator model | Explicit routing engine | Implicit (CLAUDE.md rules) | Trade-off |
| Auditability | Orchestration log + routing rules | Debate tracking only | Squad |
| Agent naming | Themed fictional (Usual Suspects) | Descriptive with personality (Archie, Tara) | Trade-off |
| SDK/type safety | `squad.config.ts` with builders | Markdown with YAML frontmatter | Squad |
| Anti-pattern detection | Organic skill accumulation | Named patterns with detection signals | vteam-hybrid |
| Human proxy | None | Pat with explicit guardrails | vteam-hybrid |
| Session continuity | Scribe + history + decisions | Handoff + MEMORY.md | Squad |
| Doc ownership | Scribe owns decision log only | Named owner per document | vteam-hybrid |
| Onboarding friction | Higher (CLI install + themed names) | Lower (template clone + descriptive names) | vteam-hybrid |
| Day-to-day convention capture | Low friction (directives) | High friction (ADR or gotchas) | Squad |

---

## Recommended Actions

Ordered by impact/effort ratio:

1. **Directives layer** (6.1) -- Closes our biggest approachability gap. Conventions should be as easy to capture as Squad's "always X" pattern. No structural changes to existing docs.

2. **Dispatch logging** (6.3) -- Closes our auditability gap. Append-only, low overhead, improves retros and session resumption.

3. **Per-agent knowledge files** (6.2) -- Closes our session continuity gap. Agents accumulate domain expertise across sessions without polluting shared docs.

4. **Skills directory** (6.4) -- Adds a portable knowledge tier we currently lack. Lower priority because our projects are typically single-repo, making portability less urgent.

Items 1-3 could be implemented as a single ADR and sprint. Item 4 is a separate, lower-priority decision.
