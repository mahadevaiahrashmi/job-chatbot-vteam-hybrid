---
agent-notes:
  ctx: "technical debt register, persists across sprints"
  deps: []
  state: stub
  last: "grace@2026-02-15"
  key: ["Grace tracks, Pat prioritizes against features"]
---
# Technical Debt Register

<!-- Grace maintains this register. Pat prioritizes debt against feature work. -->
<!-- This persists across sprints — board items get closed, but debt lives here until resolved. -->

**Project:** [Project Name]
**Last reviewed:** [Date]

## Active Debt

| ID | Description | Incurred | Why (business reason) | Est. cost to fix | Risk if left | Sprint to fix | Status |
|----|-------------|----------|----------------------|-----------------|-------------|--------------|--------|
| TD-001 | <!-- e.g. Auth module has no unit tests --> | <!-- Sprint 1 --> | <!-- Shipped MVP fast --> | <!-- M (1-2 days) --> | <!-- High: can't refactor safely --> | <!-- TBD --> | <!-- Open --> |

## Resolved Debt

| ID | Description | Incurred | Resolved | How it was fixed |
|----|-------------|----------|----------|-----------------|
| | | | | |

## Debt Categories

Tag each debt item to track patterns:

| Category | Count | Trend |
|----------|-------|-------|
| Missing tests | | |
| Hardcoded values | | |
| Missing error handling | | |
| Copy-paste duplication | | |
| Outdated dependencies | | |
| Missing docs | | |
| Performance | | |
| Security | | |
| Accessibility | | |

## Review Cadence

- **Sprint boundary:** Grace reviews the register. New debt discovered during the sprint is added. Pat decides what to pay down next sprint.
- **Every 3 sprints:** Full debt review. Re-estimate costs. Re-assess risks. Anything that's been open for 3+ sprints gets escalated.
