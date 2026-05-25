---
agent-notes: { ctx: "ADR for hybrid teams, agent consolidation, agent-notes", deps: [docs/methodology/phases.md, docs/methodology/personas.md, docs/methodology/agent-notes.md, CLAUDE.md], state: active, last: "archie@2026-02-12", key: ["three innovations in one ADR", "replaces vteam-agentapalooza fixed hierarchy"] }
---

# ADR-0003: Hybrid Team Architecture

## Status

Accepted

## Context

Three related problems emerged from real-world usage of the V-Team system across multiple projects (particularly da-clappaar sprints 1-3):

### Problem 1: Fixed hierarchy doesn't fit all phases

The original V-Team used a single organizational structure (roughly hierarchical with flat collaboration) for all work. But different development phases have fundamentally different needs:
- **Discovery** needs open brainstorming where anyone can contribute (blackboard model)
- **Implementation** needs strict handoffs in a TDD pipeline
- **Code review** needs parallel independent reviewers (ensemble model)
- **Debugging** needs shared problem-solving on a common workspace

Using the wrong org structure for a phase leads to either chaos (too loose during implementation) or bottlenecks (too structured during discovery).

### Problem 2: Too many agents with overlapping capabilities

The original roster had 32 personas. In practice:
- Many were rarely invoked (Schema Sam, Contract Cass, Breaker Bao)
- Some had overlapping capabilities that confused the coordinator (Priya vs. Tomas, Omar vs. Ines)
- Cloud specialists were triplicated across three providers with nearly identical behavior
- The coordinator often skipped agents because the roster was overwhelming

### Problem 3: Cold-start context loading is expensive

Claude Code sessions start cold. Understanding a codebase requires reading many files. Agents had no way to quickly assess a file's purpose without reading the entire thing, leading to excessive context consumption and slow ramp-up.

## Decision

Three innovations, adopted together:

### 1. Hybrid Team Methodology

Replace the fixed hierarchy with 7 phase-dependent team compositions:

| Phase | Org Model | Typical Lead |
|-------|-----------|-------------|
| Discovery | Blackboard | Cam |
| Architecture | Ensemble + Debate | Archie |
| Implementation | Pipeline (TDD) | Tara → Sato |
| Parallel Work | Market/Self-claim | Grace |
| Code Review | Ensemble (3 parallel) | Coordinator |
| Debugging | Blackboard | Sato |
| Human Interaction | Hierarchical | Cam |

The coordinator selects the appropriate phase at each transition point. Phases can nest (parallel work contains multiple implementation pipelines). See `docs/methodology/phases.md` for the full specification.

### 2. Agent Consolidation (32 → 18)

Collapse roles into capabilities. Absorbed personas don't disappear — their expertise becomes a **lens** within the consolidated agent:

| New Agent | Absorbs | Rationale |
|-----------|---------|-----------|
| **Pat** | Pat + Priya | One agent for "what to build and why" |
| **Grace** | Grace + Tomas | One agent for "where are we and what's blocking" |
| **Archie** | Archie + Sam + Cass | System design is one capability (architecture + data + API) |
| **Dani** | Dani + Uma | User-facing design is one capability (design + accessibility) |
| **Pierrot** | Pierrot + RegRaj | Risk assessment is one capability (security + compliance) |
| **Ines** | Ines + Omar + Bao | "Everything between git push and production" is one capability |
| **Cloud Architect** | azure/aws/gcp-architect | One architect adapts to target cloud |
| **Cloud CostGuard** | azure/aws/gcp-costguard | One cost analyst adapts to target cloud |
| **Cloud NetDiag** | azure/aws/gcp-netdiag | One diagnostician adapts to target cloud |

Unchanged: Cam, Sato, Tara, Vik, Code Reviewer, Diego, Wei, Debra, User Chorus.

Result: 18 agent definitions (15 individuals + 1 composite + 3 cloud-adaptive), down from 32. See `docs/methodology/personas.md` for the full roster.

### 3. Agent-Notes Protocol

Structured metadata at the top of every file (except pure JSON) that bootstraps agent context:

```yaml
---
agent-notes: { ctx: "purpose <10 words", deps: [file1, file2], state: active, last: "agent@date" }
---
```

Format adapts to file type (YAML frontmatter for .md, single-line comment for code, HTML comment for Svelte/agent files). See `docs/methodology/agent-notes.md` for the full specification.

## Consequences

### Positive

- **Phase-appropriate structure**: Each development phase uses the org model that fits it best.
- **Fewer, more capable agents**: 18 agents is manageable. The coordinator can hold the full roster in mind.
- **Preserved expertise**: No knowledge is lost — absorbed personas become lenses within consolidated agents.
- **Faster context loading**: Agent-notes let agents decide whether to read a file before opening it.
- **Better cloud support**: One cloud architect that adapts is more maintainable than three nearly-identical specialists.
- **Lessons learned baked in**: Sprint retrospective findings from da-clappaar are codified into the methodology.

### Negative

- **Consolidated agents are more complex**: Archie with three lenses (architecture + data + API) has a longer agent definition and more to track.
- **Phase selection requires judgment**: The coordinator must correctly identify phase transitions. Bad phase selection leads to wrong team composition.
- **Agent-notes require discipline**: Every file edit must update the `last` field. This is easy to forget.
- **Migration cost**: Existing projects using vteam-agentapalooza need to update agent references (e.g., `sam` → `archie`, `uma` → `dani`).

### Neutral

- The hybrid model doesn't prevent invoking agents outside their typical phase — it just provides defaults.
- Agent-notes are designed to be ignorable by humans — they're for agents, not for code review.
- The consolidation map is documented so future splits (e.g., re-separating Sam from Archie for a data-heavy project) are straightforward.
