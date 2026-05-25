---
agent-notes: { ctx: "ADR for README swap pattern, storefront vs child placeholder", deps: [README.md, README-template.md, docs/adrs/template/0005-template-restructure.md], state: accepted, last: "archie@2026-03-21" }
---

# ADR-0006: README Swap Pattern — Storefront README for Template, Placeholder for Children

## Status

Accepted (2026-03-21)

## Context

ADR-0005 established that `README.md` should be a "replaceable stub" and the selling content should live in `docs/template-guide.md`. This solved the dual-audience problem (template browsers vs project developers) but created a new one: **first-contact users only see README.md on GitHub**.

The stub README loses prospective users in 30 seconds. The value proposition, conversation example, agent roster, and sprint lifecycle diagrams — all excellent content in `docs/template-guide.md` — are invisible unless someone clicks through.

### Competitive context

Analysis of [bradygaster/squad](https://github.com/bradygaster/squad) (1,039 stars in 6 weeks) showed that their single-file README with progressive disclosure is a major adoption driver. Squad's "Quick Start" with validation checkpoints gets users to value in under 2 minutes. Our stub README followed by 11 process docs cannot compete on first impression.

### Constraint

This is a GitHub repo template. `README.md` propagates to every child repo created from it. A rich README in the template becomes unwanted boilerplate in child projects. We have been down this path before (the original `README-template.md` approach).

## Decision

### Swap pattern: two READMEs, swapped during initialization

- **`README.md`** — Rich storefront content adapted from `docs/template-guide.md`. This is what GitHub displays to prospective users visiting the template repo. Contains value proposition, quick start, 5 core agents, sprint lifecycle, command reference, and directory tree.

- **`README-template.md`** — Child project placeholder. Contains `[Your Project Name]`, getting started steps, and "Replace this README" instruction. This is what child projects should use.

- **Both `/kickoff` and `/scaffold-*` commands** execute `mv README-template.md README.md` as their first step. This ensures child projects get the clean placeholder regardless of which entry path the user takes.

### Why kickoff, not just scaffold

Users often skip scaffold and go directly to `/kickoff`. The swap must happen in both paths to prevent child projects from inheriting the storefront README.

### Relationship to template-guide.md

`docs/template-guide.md` remains the persistent deep-dive reference (customization, scaling, learning path). The storefront README links to it for users who want more detail. Content is adapted, not duplicated — the README is a condensed, progressive-disclosure version optimized for scanning.

## Consequences

### Positive

- Template repo visitors see a compelling README that explains the value proposition
- Child repos get a clean placeholder (same as today's behavior, just via swap)
- No change to `docs/template-guide.md` — it continues to be the deep reference
- Both entry paths (scaffold and kickoff) are covered

### Negative

- Two README files in the template repo (minor clutter)
- Scaffold and kickoff commands each need a swap step (low maintenance burden)
- If a user runs neither scaffold nor kickoff, they inherit the storefront README (acceptable — the "Replace This README" section at the bottom of the storefront mitigates this)

### Amends

This amends ADR-0005's decision #1 (Entry Points). ADR-0005 moved the rich content to `docs/template-guide.md` and kept README as a stub. This ADR reverses that for the template repo's README while preserving the template-guide as the persistent reference.
