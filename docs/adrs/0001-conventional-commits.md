---
agent-notes: { ctx: "ADR mandating conventional commit format", deps: [CLAUDE.md], state: active, last: "archie@2026-02-12" }
---

# ADR-0001: Use Conventional Commits

## Status

Accepted

## Context

We need a consistent commit message format that communicates the nature of changes clearly, supports automated changelog generation, and works well with semantic versioning.

## Decision

All commits in this project will follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

Allowed types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`, `perf`, `style`, `build`.

Scopes are optional but encouraged when they add clarity (e.g., `feat(auth): add login endpoint`).

## Consequences

### Positive

- Commit history is scannable and meaningful.
- Enables automated changelog and version bumping tooling in the future.
- Clear communication of intent in every commit.
- Consistent across all projects using this template.

### Negative

- Contributors must learn and follow the format.

### Neutral

- Commit hooks or CI checks can be added later to enforce the convention.
