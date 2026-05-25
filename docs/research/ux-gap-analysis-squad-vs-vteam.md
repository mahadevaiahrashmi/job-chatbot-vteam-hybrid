---
agent-notes: { ctx: "UX gap analysis comparing Squad and vteam-hybrid interaction design", deps: [docs/methodology/phases.md, docs/methodology/personas.md, docs/process/team-governance.md, docs/research/what-we-learn-from-hve-core.md], state: active, last: "dani@2026-03-21" }
---

# UX Gap Analysis: Squad vs vteam-hybrid

> **Author:** Dani (Design + UX + Accessibility)
> **Date:** 2026-03-21
> **Status:** Research -- not yet implemented
> **Source:** [bradygaster/squad](https://github.com/bradygaster/squad) vs vteam-hybrid template system

This analysis examines interaction design differences between Squad's CLI-shell model and our CLAUDE.md-driven template model. The goal is concrete, implementable improvements -- not "make it prettier."

---

## 1. Information Architecture: Progressive Disclosure vs Front-Loading

### What Squad does

Squad uses a **funnel model** for complexity:

1. `squad init` -- a single command scaffolds everything. The user answers a few questions, and the system creates agent charters, config, and project structure. Zero pre-reading required.
2. `squad` (no args) -- drops into an interactive shell. The shell itself teaches the user through tab completion and help text.
3. `/commands` -- discoverable inside the shell, not in a README.
4. Advanced features (`--yolo`, `triage`, `watch`, `loop`) -- discovered through usage, not upfront documentation.

The user learns by doing. Each layer is hidden until the previous one is mastered.

### What we do

Our system uses a **front-loaded model**:

1. Create repo from GitHub template -- this produces a repo with 25+ markdown files, 19 agent definitions, 25 slash commands, and a CLAUDE.md that references 10+ other documents.
2. The user is expected to read CLAUDE.md (150+ lines), which references `docs/methodology/phases.md`, `docs/methodology/personas.md`, `docs/process/team-governance.md`, and more.
3. The Session Entry Protocol requires the user to answer three questions before writing any code.
4. Phase selection, agent invocation, and workflow are all documented but not guided.

### The UX cost

**Cognitive load at entry.** A new user faces CLAUDE.md's 150 lines, a Phase Selection Flowchart, a 7-phase model with 18 agents, and governance rules they need to internalize before writing a line of code. Squad's equivalent moment is: `squad init`. The information asymmetry at the onboarding boundary is significant.

**The "which doc do I read?" problem.** Our Process Docs Index lists 12 documents. A user who wants to know "how do I start?" must mentally trace the path: CLAUDE.md -> Session Entry Protocol -> /kickoff -> phases.md -> personas.md. Squad's equivalent: type `squad`.

### Concrete improvements

**A. Create a `/start` or `/init` command.** This would be the single entry point for new projects -- equivalent to `squad init`. It would:
- Detect whether this is a fresh-from-template repo or an existing project.
- If fresh: run the essential setup (repo name, tech stack, initial scaffolding), then hand off to `/kickoff` for discovery.
- If existing: run `/resume` automatically.
- The user never needs to read CLAUDE.md first. The command bootstraps context.

**B. Introduce a "Phase 0: Orientation" in CLAUDE.md.** Before the Session Entry Protocol's three questions, add: "If this is your first session, run `/kickoff`. If you're continuing, run `/resume`. Everything else flows from there." Two sentences, two paths, zero ambiguity.

**C. Lazy-load governance docs.** Instead of the Process Docs Index listing 12 documents upfront, have each slash command pull in its relevant governance docs when invoked. The user learns about the Architecture Gate when `/adr` is invoked, not when they first open CLAUDE.md. This is what Squad's shell does -- it teaches at the moment of relevance.

---

## 2. The Shell as a UX Innovation

### What Squad does

Squad's interactive shell is a **persistent interaction context**. You type `squad` and you're in a mode where:
- Tab completion shows available commands.
- `@AgentName` directs messages to specific agents.
- The shell maintains session state -- you don't re-explain context.
- Status indicators show agents working in real-time.
- It is the primary interface. You live in it.

### What we have instead

Claude Code itself is already a persistent interactive session. We don't need to build a shell -- we have one. But we don't treat it as one.

Our interaction model is **command-invocation based**: the user types `/kickoff`, `/sprint-boundary`, `/handoff`. Between commands, the user interacts with the coordinator directly using natural language. There is no `@agent` addressing -- the coordinator decides which agents to invoke based on rules.

### Could we have a shell equivalent?

**We already do, and it is Claude Code.** The gap is not the shell itself -- it is the discoverability and guidance layer on top of it. Squad's shell teaches you what's possible. Claude Code's session is open-ended, which is powerful but disorienting for new users.

### Concrete improvements

**D. A `/help` command that acts as a context-sensitive guide.** Based on the current project state (fresh template? mid-sprint? post-handoff?), it shows the 2-3 most relevant next actions. Examples:
- Fresh repo: "Run `/kickoff <your idea>` to start discovery."
- Mid-sprint, no handoff: "You have 3 items in progress. Continue with issue #X or run `/handoff` to save state."
- Post-sprint: "Sprint 2 is complete. Run `/sprint-boundary` to close it out."

This is progressive disclosure in action: the right information at the right time.

**E. A `/status` command (lightweight, non-blocking).** Squad has real-time status visibility. We have... nothing mid-session unless you ask Grace. A `/status` command would:
- Show current sprint, wave, and active items.
- Show which agents were last invoked and what they found.
- Show pending decisions (blocked items, proxy decisions awaiting review).
- Take < 5 seconds to run (read handoff + board state, no subagent spawning).

---

## 3. Agent Addressability: `@AgentName` vs Rule-Based Invocation

### What Squad does

Users type `@Architect design the auth system` and the message is routed to that agent. It is direct, intentional, and feels like talking to a person on a team.

### What we do

Our system has two modes:
1. **Rule-based invocation:** The coordinator reads the situation and invokes the right agents based on persona triggers in `docs/process/team-governance.md`. The user doesn't need to know agent names.
2. **Explicit invocation:** The user says "invoke the team" or "have Cam review this" and the coordinator spawns subagents.

### Which feels better?

**Both models have real advantages, and the right answer is to support both.**

Rule-based invocation is better for novices and for correctness. A new user doesn't know they need Wei to challenge their architecture. The system knowing this for them is a genuine UX win -- it is the equivalent of a junior developer having a senior architect who automatically reviews their design decisions. Squad's `@Architect` model requires the user to know their team, which is powerful but assumes expertise.

Explicit `@Agent` addressing is better for experienced users who know the team and want precision. "I want Pierrot specifically to look at this endpoint" is a valid, useful interaction that our system supports but doesn't make ergonomic.

### The gap

Our system supports explicit invocation, but the syntax is clunky. The user must say "have Pierrot review this" in natural language, and the coordinator must parse intent and spawn the right subagent. There is no shorthand, no tab completion, no visual confirmation that the right agent was invoked.

### Concrete improvements

**F. Document the `@agent` invocation pattern explicitly.** In CLAUDE.md, add a section: "To invoke a specific agent, address them by name: 'Pierrot, review this endpoint for security concerns.' The coordinator will spawn them as a subagent." This makes the implicit explicit.

**G. Create per-agent shortcut commands for common invocations.** Beyond the existing `/design` (Dani) and `/code-review` (composite), add:
- `/challenge <topic>` -- invokes Wei to challenge a decision.
- `/threat-model` -- invokes Pierrot for security review.
- `/explain <topic>` -- invokes Prof to explain a decision or pattern.

These are ergonomic shortcuts for experienced users who know what they want.

**H. Show which agents are active when they're invoked.** When the coordinator spawns subagents, the output should clearly identify which agent is speaking. Our governance doc says agent voice should come through -- but there is no structural signal. A line like "--- Pierrot (Security + Compliance) ---" before their output would help. Squad uses emoji badges per role -- we should at minimum use clear text headers.

---

## 4. Visibility and Feedback

### What Squad does

- Status badges and emoji per agent role.
- Progress indicators showing agents working in parallel.
- Real-time visibility: you can see what's happening.
- `decisions.md` visible to all agents and humans.
- `orchestration-log/` captures routing decisions.

### What we do

- Agent output appears inline in the Claude Code session.
- No progress indicators for parallel agent work.
- Tracking artifacts exist (`docs/tracking/`) but are produced after the fact, not during.
- No equivalent of `decisions.md` as a live document -- our ADRs and tracking artifacts serve this role but are heavier weight.
- The handoff file captures state at session boundaries, not during sessions.

### The gap

**Mid-session visibility is our weakest point.** When the coordinator spawns three parallel code reviewers, the user sees... eventually... a synthesized result. There is no "Vik is reviewing... Tara is checking tests... Pierrot is scanning for vulnerabilities..." feedback loop. The user waits in the dark.

**Decision visibility is a gap.** Squad's `decisions.md` is a living document that accumulates every decision as it happens. Our tracking artifacts are produced at phase boundaries -- there is a temporal gap between when a decision is made and when it is recorded.

### Concrete improvements

**I. Structured output headers for subagent work.** When the coordinator synthesizes subagent output, use a consistent format:

```
## Code Review Results

### Vik (Simplicity + Maintainability)
[findings]

### Tara (Test Coverage)
[findings]

### Pierrot (Security + Compliance)
[findings]

### Synthesis
[combined findings by severity]
```

This is zero-cost (just formatting discipline) and immediately improves visibility.

**J. A live decisions log.** Create a `docs/decisions-log.md` file (lighter than ADRs, heavier than tracking artifacts) that captures decisions as they happen during a session. One line per decision: "Chose X over Y because Z." This is the "Key Decisions" section from our tracking protocol, but promoted to a standalone file that accumulates across sessions. It serves the same purpose as Squad's `decisions.md`.

**K. Progress narration for parallel work.** When spawning parallel subagents, the coordinator should narrate: "Launching three parallel reviewers: Vik (simplicity), Tara (tests), Pierrot (security). Results will be synthesized below." This sets expectations. It is the text equivalent of Squad's progress indicators.

---

## 5. Error Recovery and Self-Service: `squad doctor` vs Nothing

### What Squad does

- `squad doctor` -- a diagnostic command that checks environment, config, agent health, and API connectivity.
- First-run gating -- the system refuses to proceed without valid setup.
- Hostile input testing -- the system handles bad input gracefully.
- 15 commands with clear aliases -- multiple ways to express the same intent.

### What we do

- The `/resume` command has a pre-flight check (GitHub CLI auth, board access).
- `/sprint-boundary` Step 0 has a blocking pre-flight gate.
- `/kickoff` Phase 5 checks GitHub access before board creation.
- There is no general-purpose diagnostic command.
- There is no first-run gating -- the system assumes CLAUDE.md has been read.
- Error handling for bad state is scattered across individual commands.

### The gap

**No unified diagnostic command.** If something is wrong (GitHub auth expired, board misconfigured, missing status options, stale handoff), the user discovers it when a command fails mid-execution. Squad's `squad doctor` catches these problems proactively.

**No first-run detection.** A user who creates a repo from our template and starts typing without reading CLAUDE.md will get no warning. They'll hit Session Entry Protocol violations and wonder why the system is asking them questions about work items before they've even described their project.

### Concrete improvements

**L. Create a `/doctor` command.** It checks:
- Is this a fresh-from-template repo? (No `docs/product-context.md`, no `docs/plans/`, no handoff.) If so: "This looks like a new project. Run `/kickoff <your idea>` to get started."
- Is GitHub CLI authenticated? Can we access the project board?
- Are all 5 board statuses configured?
- Is there a stale handoff file? (Last modified > 7 days ago.)
- Are there uncommitted changes?
- Are there orphaned tracking artifacts (status: Active but referenced sprint is complete)?
- Is `docs/code-map.md` present? (If not, the orientation step will fail.)

This command costs almost nothing to build and catches the class of errors that currently surface mid-workflow.

**M. First-run detection in CLAUDE.md.** Add a conditional instruction at the very top of CLAUDE.md:

```
If no `docs/product-context.md` exists and no `.claude/handoff.md` exists, this is a new project.
Before doing anything else, run `/kickoff <user's request>`.
Do not apply the Session Entry Protocol -- kickoff handles it.
```

This is a two-line addition that prevents the most common onboarding failure mode.

---

## 6. The "Stepping Away" Problem

### What Squad does

- `decisions.md` -- a persistent record of what was decided and why.
- `orchestration-log/` -- routing decisions, which agent handled what.
- `log/` -- full session logs.
- Session persistence with crash resume from checkpoint.

When you step away from Squad and come back, the breadcrumb trail is comprehensive. You can reconstruct what happened, why, and where it left off.

### What we do

- `.claude/handoff.md` -- written on `/handoff`, captures session state.
- `docs/tracking/` -- phase tracking artifacts with Key Decisions sections.
- `docs/sprints/sprint-N-plan.md` -- sprint plans with wave breakdowns.
- `docs/retrospectives/` -- sprint retros.
- `docs/adrs/` -- architecture decisions.

### The gap

**Our breadcrumb trail is strong but requires active invocation.** The handoff is written when the user runs `/handoff`. The tracking artifacts are written at phase boundaries. If the user steps away without running `/handoff` -- because their session timed out, because they forgot, because Claude ran out of context -- the breadcrumb trail has a gap.

Squad's session persistence handles crashes automatically. Our system does not.

**No orchestration log.** We have no equivalent of Squad's `orchestration-log/`. When the coordinator routes a message to an agent or makes a phase transition, there is no record of the routing decision itself. The output of the agent is captured, but not the "why this agent, why now" reasoning.

### Concrete improvements

**N. Auto-handoff on context exhaustion warning.** If the coordinator detects that context is running low (the session is nearing its limit), it should automatically run `/handoff` before the session ends. This is the crash-resume equivalent for our context-limited world.

**O. Lightweight orchestration notes.** When the coordinator makes a routing decision (invoking agents, transitioning phases), append a one-line note to a `docs/tracking/session-log.md` file:
- `[14:32] Phase transition: Discovery -> Architecture (human confirmed vision)`
- `[14:35] Invoked: Wei (standalone) to challenge ADR-005`
- `[14:40] Invoked: Vik + Tara + Pierrot (parallel) for code review`

This is lower-overhead than Squad's full orchestration log, but captures the routing decisions that currently vanish.

**P. "Where was I?" recovery.** If a user starts a session without running `/resume` (they just open Claude Code and start talking), the coordinator should detect the existence of `.claude/handoff.md` and proactively suggest: "I see a handoff from [date]. Would you like me to resume from there, or are you starting fresh?" This is the self-healing equivalent of Squad's crash resume.

---

## 7. Accessibility and Inclusivity

### What Squad does

Squad's CLI uses emoji extensively for agent identity (architect icon, tester icon, etc.), color-coded output, and status badges. This is visually rich but raises concerns:
- Emoji as the primary identifier for agents is problematic for screen readers. Emoji descriptions are often unhelpful ("hammer and wrench" for a builder agent) and add noise.
- Color-coded status assumes the user can perceive color. No evidence of colorblind-safe palettes.
- CLI output formatting may not survive piping or text-to-speech.

### What we do

Our system is text-based (markdown files and Claude Code's chat interface), which is inherently more accessible:
- Agent output is identified by name in text, not by emoji.
- No color dependencies for information.
- All artifacts are plain markdown -- universally parseable.

However:
- Our Mermaid diagrams (Phase Selection Flowchart) have no text alternative for users who cannot render them.
- Our agent-notes protocol uses dense, compressed syntax that may be difficult for users with cognitive accessibility needs to parse -- though this is agent-facing, not human-facing.

### Observations

**Squad optimizes for visual delight at the cost of accessibility.** Our system optimizes for content accessibility at the cost of visual engagement. Neither is fully right.

### Concrete improvements

**Q. Add text alternatives for Mermaid diagrams.** Every Mermaid diagram in our docs should have a text description below it summarizing the same information. The Phase Selection Flowchart in `docs/methodology/phases.md` is a key example -- it encodes critical routing logic that is invisible to users who cannot render Mermaid.

**R. Human-facing summaries of agent-notes.** Agent-notes are for agents, not humans -- this is documented and correct. But if a human reads a file and sees `{ ctx: "P1 design + UX + accessibility", deps: [...], state: canonical, last: "archie@2026-02-12" }`, they should be able to make sense of it. A one-line comment in the agent-notes spec explaining the format for human readers would help.

**S. If we ever build visual status indicators (improvement K), ensure they degrade gracefully to text.** Avoid the trap Squad fell into of using emoji as primary identifiers. Use text first, visual enhancement second.

---

## Summary of Proposed Improvements

### Priority 1: Low effort, high UX impact

| ID | Improvement | Effort | Impact |
|----|------------|--------|--------|
| B | "Phase 0: Orientation" -- two lines in CLAUDE.md | Trivial | Eliminates onboarding confusion |
| F | Document `@agent` invocation pattern in CLAUDE.md | Trivial | Makes implicit pattern explicit |
| I | Structured output headers for subagent work | Trivial | Immediate visibility improvement |
| K | Progress narration for parallel work | Trivial | Sets expectations during waits |
| M | First-run detection in CLAUDE.md | Trivial | Prevents most common onboarding failure |
| P | "Where was I?" recovery detection | Low | Self-healing session continuity |
| Q | Text alternatives for Mermaid diagrams | Low | Accessibility compliance |

### Priority 2: Medium effort, significant UX improvement

| ID | Improvement | Effort | Impact |
|----|------------|--------|--------|
| A | `/start` or `/init` command | Medium | Single entry point, matches Squad's `squad init` |
| D | Context-sensitive `/help` command | Medium | Progressive disclosure, right info at right time |
| E | Lightweight `/status` command | Medium | Mid-session visibility |
| J | Live decisions log | Medium | Decision visibility across sessions |
| L | `/doctor` diagnostic command | Medium | Proactive error detection |
| N | Auto-handoff on context exhaustion | Medium | Crash-resume equivalent |

### Priority 3: Lower priority or higher effort

| ID | Improvement | Effort | Impact |
|----|------------|--------|--------|
| C | Lazy-load governance docs per command | High | Reduces CLAUDE.md size; structural change |
| G | Per-agent shortcut commands | Medium | Ergonomic for power users |
| H | Agent identity headers in output | Low | Visual clarity |
| O | Lightweight orchestration notes | Medium | Audit trail for routing decisions |
| R | Human-readable agent-notes commentary | Trivial | Minor accessibility improvement |
| S | Graceful degradation for visual indicators | N/A | Design principle for future work |

---

## Design Philosophy Observation

The fundamental difference between Squad and vteam-hybrid is not features -- it is **who carries the burden of understanding.**

Squad says: "The system will teach you as you go. Start here. We'll figure it out together."

vteam-hybrid says: "Read the documentation. Understand the methodology. Then the system will enforce it."

Squad optimizes for **onboarding delight**. We optimize for **execution rigor**. Both are valid, but they serve different moments in the user journey. The improvements above are not about becoming Squad -- they are about reducing the tax we impose on the first 10 minutes without sacrificing the rigor that makes the next 10 sprints work.

The most impactful single change would be improvements B + M together: a two-line orientation clause in CLAUDE.md that detects new projects and routes them to `/kickoff`, combined with first-run detection that prevents the Session Entry Protocol from firing on an uninitialized project. This alone would transform our onboarding from "read 150 lines of documentation" to "run one command."
