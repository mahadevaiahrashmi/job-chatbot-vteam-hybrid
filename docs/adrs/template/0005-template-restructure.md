---
agent-notes: { ctx: "ADR for docs restructure, tool decoupling, newcomer UX", deps: [CLAUDE.md, README.md, docs/methodology/phases.md, docs/methodology/personas.md], state: accepted, last: "archie@2026-02-21", key: ["3 file moves not 8", "no abstract tracking ops layer", "phased migration one commit per move"] }
---

# ADR-0005: Template Restructure — Navigation, Tool Decoupling, CLAUDE.md Simplification

## Status

Accepted (post Archie-Wei debate, 2026-02-21)

## Context

### The Three Problems

The vteam-hybrid template has real users (colleagues in the organization, plus a future customer needing Jira). User feedback and competitive analysis (SpecKit, HVE Core) reveal three interrelated problems:

**Problem 1: Newcomer Navigation (PRIMARY).** A new user opening this repo must absorb 18 personas, 7 phases, debate protocols, and agent-notes before doing anything. Three entry points (README.md, README-template.md, CLAUDE.md) with unclear sequencing. Stub/template files sit at the same level as substantive methodology files. SpecKit and HVE Core let you DO something in ~5 minutes; vteam-hybrid requires ~30 minutes of reading.

**Problem 2: Tool Coupling (REAL).** The `gh` CLI is hardcoded into 11 files (~45 occurrences). The methodology is tool-agnostic, but the implementation is welded to GitHub Projects.

**Problem 3: CLAUDE.md Overload (SECONDARY).** CLAUDE.md is ~220 lines combining orientation, process rules, board commands, sprint workflow, session management, and a 21-entry command table.

### Design Constraints

1. Keep what makes vteam-hybrid unique: deep persona system, adversarial debate, phase-dependent teams.
2. Must work as both a template in isolation and a project built from it.
3. Agent-notes protocol preserved.
4. `.claude/agents/` and `.claude/commands/` are fixed by Claude Code conventions.

### Architecture Gate

This ADR went through the mandatory Archie-Wei debate (2026-02-21). Wei challenged 5 aspects of the original design. Archie accepted 3 fully, partially accepted 2. The design below reflects the post-debate resolution. See debate summary in Section 8.

## Decision

### 1. Entry Points: Stub README + Persistent Template Guide

**Before:** Three entry points (README.md stub, README-template.md reference, CLAUDE.md process manual).

**After:** README.md remains a replaceable stub (gets overwritten after scaffolding). Template reference material moves to `docs/template-guide.md` (persists under docs/). CLAUDE.md slims to ~100 lines.

```
README.md              -- Quickstart stub (replaced by project README after scaffold)
docs/template-guide.md -- Persistent template reference (learning path, customization)
CLAUDE.md              -- Slim agent-facing runtime instructions
```

README-template.md is deleted. Its content moves to `docs/template-guide.md`.

**Rationale (from Wei Challenge 5):** A mega-README that serves template browsers, template users, AND project developers serves none well. The stub README gets replaced after scaffolding; the template guide persists because it lives under docs/.

### 2. Docs Hierarchy: One New Directory (methodology/)

**Before:** Flat `docs/` with methodology files, stubs, and process docs mixed together.

**After:** Only `docs/methodology/` is created. Stub files stay in `docs/` root.

```
docs/
  methodology/              -- "Read this to understand the system"
    phases.md               -- 7-phase model (was hybrid-teams.md)
    personas.md             -- 18-agent roster (was team_personas.md)
    agent-notes.md          -- Protocol spec (was agent-notes-protocol.md)

  process/                  -- "Reference when doing work" (unchanged)
  integrations/             -- Tracking adapters (new, see below)
  adrs/                     -- Architecture decisions (unchanged)
  tracking/                 -- Phase artifacts (unchanged)
  code-map.md               -- Stub (stays in docs/ root)
  test-strategy.md          -- Stub (stays in docs/ root)
  tech-debt.md              -- Stub (stays in docs/ root)
  performance-budget.md     -- Stub (stays in docs/ root)
  config-manifest.md        -- Stub (stays in docs/ root)
  ...                       -- Other dirs unchanged
```

**3 file moves, not 8.** Only methodology files move. Stubs stay put.

**Rationale (from Wei Challenge 2):** Agents follow explicit file paths and don't benefit from directory hierarchy. The newcomer problem is primarily a README/learning-path problem, not a directory structure problem. However, `docs/methodology/` earns its keep by separating "the system you are using" (don't customize) from "your project's artifacts" (do customize). People in downstream repos have edited `hybrid-teams.md` thinking it was project-specific.

### 3. TL;DR Instead of Separate Overview

No separate `docs/methodology/overview.md`. Instead, a 15-line TL;DR section at the top of `docs/methodology/phases.md`.

**Rationale (from Wei Challenge 4):** A separate overview.md would have no owner, no update trigger, and no agent that reads it. It would rot by sprint 5. The TL;DR lives in the same file as the detail, so it gets reviewed whenever phases change.

### 4. Integration Adapters: Concrete Files, No Abstract Layer

```
docs/integrations/
  README.md              -- Which adapter is active, how to switch
  github-projects.md     -- Concrete gh CLI recipes
  jira.md                -- Concrete Jira CLI/API recipes
```

No `tracking-operations.md`. No abstract operations vocabulary. Agents and commands reference the concrete adapter file directly. The README switchboard tells them which file to read.

CLAUDE.md gets:
```markdown
## Tracking
<!-- tracking-adapter: github-projects -->
Adapter docs: `docs/integrations/README.md`
Status flow: Backlog → Ready → In Progress → In Review → Done
```

**Rationale (from Wei Challenge 3):** An abstract operations layer for exactly 2 implementations is premature abstraction. Two concrete files + one switchboard README achieves 90% of the value at 25% of the complexity. If a third adapter is needed, extract the abstraction then.

### 5. CLAUDE.md Simplification: ~220 → ~100 Lines

**Moves out:**

| Section | Lines | Destination | Rationale |
|---------|-------|-------------|-----------|
| Board Status Commands | 15 | `docs/integrations/github-projects.md` | Tool-specific |
| Custom Commands table | 21 | Removed (auto-discovered by Claude Code) | Redundant, drifts |
| Architecture Gate detail | 12 | Already in `docs/process/team-governance.md` | Duplicated |
| Proxy Mode detail | 5 | Already in `docs/process/gotchas.md` | Duplicated |
| Sprint Boundary steps | 10 | Already in the command file | Duplicated |

**Stays:** Project Overview, Agent-Notes mandate, Team summary table, Critical Rules (condensed), Development Workflow, Tracking config, Session Management, Process Docs Index, Project Structure tree.

### 6. File Move/Change Map

| Current Path | New Path | Change |
|---|---|---|
| `docs/hybrid-teams.md` | `docs/methodology/phases.md` | **Move** + add TL;DR |
| `docs/team_personas.md` | `docs/methodology/personas.md` | **Move** |
| `docs/agent-notes-protocol.md` | `docs/methodology/agent-notes.md` | **Move** |
| `README-template.md` | `docs/template-guide.md` | **Move + rename** |
| `README.md` | `README.md` | **Rewrite** (quickstart stub) |
| `CLAUDE.md` | `CLAUDE.md` | **Simplify** (~220 → ~100 lines) |
| (new) | `docs/integrations/README.md` | **Create** |
| (new) | `docs/integrations/github-projects.md` | **Create** |
| (new) | `docs/integrations/jira.md` | **Create** |

### 7. Cross-Reference Impact

~90 reference updates across ~30 files (primarily agent-notes `deps` arrays and inline path mentions). Executed as phased migration:

| Phase | Commit | Files touched |
|---|---|---|
| A | Create new dirs + new files | 0 existing files |
| B1 | Move hybrid-teams.md → methodology/phases.md + update refs | ~20 files |
| B2 | Move team_personas.md → methodology/personas.md + update refs | ~25 files |
| B3 | Move agent-notes-protocol.md → methodology/agent-notes.md + update refs | ~5 files |
| C | Simplify CLAUDE.md | 1 file |
| D | Rewrite README.md, move README-template.md → template-guide.md | 2 files |

Each commit is grep-validated: `grep -r '<old-path>' --include='*.md'` must return zero results before committing.

## Consequences

### Positive

- Newcomer UX improved: clear learning path, methodology separated from stubs.
- Tool decoupled: adding Jira (or Linear) means one adapter file, not editing 11 files.
- CLAUDE.md halved: context window savings on every session.
- Methodology docs signaled as "system, don't customize" by directory placement.

### Negative

- ~90 cross-reference updates across ~30 files. Mitigated by phased commits + grep validation.
- Extra indirection for tracking: agents read adapter file once per session.
- Jira adapter is untested — needs real Jira instance to validate.

### Neutral

- All 18 agents and 21+ commands preserved in substance.
- Agent-notes format unchanged.
- Existing downstream projects unaffected.

## 8. Debate Summary (Archie vs Wei)

| # | Wei's Challenge | Archie's Response | Outcome |
|---|---|---|---|
| 1 | Blast radius understated (170 refs in 54 files, not "20+") | **Accept.** Withdraw atomic commit. Phased migration, one file per commit, grep-validated. | Design changed |
| 2 | Four-tier hierarchy solves wrong problem (agents don't browse dirs) | **Partially accept.** Reduce to one new dir (methodology/). Drop docs/project/. 3 moves not 8. | Design changed |
| 3 | Adapter pattern over-engineered (abstract ops for 2 implementations) | **Partially accept.** Drop tracking-operations.md. Keep 3 files (README + 2 concrete adapters). | Design changed |
| 4 | overview.md will rot (no owner, no update trigger) | **Accept.** Eliminate overview.md. 15-line TL;DR at top of phases.md. | Design changed |
| 5 | README consolidation conflates audiences (browser vs user vs developer) | **Accept.** Keep README as replaceable stub. Move template guide to docs/template-guide.md. | Design changed |

## Implementation Plan

1. Create `docs/methodology/`, `docs/integrations/`. Write new files.
2. Move `hybrid-teams.md` → `methodology/phases.md`. Update all refs. Commit. Grep-verify.
3. Move `team_personas.md` → `methodology/personas.md`. Update all refs. Commit. Grep-verify.
4. Move `agent-notes-protocol.md` → `methodology/agent-notes.md`. Update all refs. Commit. Grep-verify.
5. Create integration adapter files. Extract `gh` recipes from CLAUDE.md.
6. Simplify CLAUDE.md. Commit.
7. Rewrite README.md. Move README-template.md → `docs/template-guide.md`. Commit.
