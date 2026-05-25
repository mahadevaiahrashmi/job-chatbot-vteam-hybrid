---
agent-notes: { ctx: "ADR mandating TDD red-green-refactor cycle", deps: [CLAUDE.md], state: active, last: "archie@2026-02-12" }
---

# ADR-0002: Test-Driven Development Workflow

## Status

Accepted

## Context

We want a development process that produces well-tested, well-designed code by default and catches regressions early.

## Decision

All feature and fix work will follow the TDD cycle:

1. **Red** — Write a failing test that describes the desired behavior.
2. **Green** — Write the minimum code to make the test pass.
3. **Refactor** — Clean up the code while keeping tests green.

Tests are not an afterthought; they are the entry point for every change. For items sized M or larger, Tara must be invoked as a standalone agent to write the failing tests before Sato implements. For S and XS items, the implementing agent may write tests inline, but the red-green-refactor discipline still applies.

## Consequences

### Positive

- High test coverage by default.
- Tests serve as living documentation of behavior.
- Encourages small, incremental steps and better design.
- Separating test authorship (Tara) from implementation (Sato) strengthens the feedback loop.

### Negative

- Initial development may feel slower until the habit is established.
- Requires discipline to not skip the "red" phase on small changes.

### Neutral

- The specific testing framework will be chosen when the tech stack is defined.
