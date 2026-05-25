---
agent-notes:
  ctx: "who owns which docs, update rules"
  deps: [CLAUDE.md]
  state: active
  last: "coordinator@2026-02-15"
---
# Document Ownership

Extracted from CLAUDE.md to reduce context window load. Referenced by CLAUDE.md Process Docs Index.

## Ownership Table

| Doc | Owner | Path | Update trigger |
|-----|-------|------|---------------|
| SBOM + dependency decisions | Pierrot | `docs/sbom/sbom.md`, `docs/sbom/dependency-decisions.md` | Dependency add/remove/upgrade |
| Threat model | Pierrot | `docs/security/threat-model.md` | New endpoints, data types, integrations, auth flows |
| Performance budget | Vik (review) / Ines (verify) | `docs/performance-budget.md` | System evolution |
| Test strategy | Tara | `docs/test-strategy.md` | New test patterns or coverage targets |
| Technical debt | Grace (track) / Pat (prioritize) | `docs/tech-debt.md` | Sprint boundaries, shortcuts taken |
| Runbooks | Ines | `docs/runbooks/` | New infrastructure or alerts |
| Config manifest | Ines | `docs/config-manifest.md` | New env vars, feature flags, config files |
| Changelog | Diego | `CHANGELOG.md` | Releases |
| Code map | Coordinator | `docs/code-map.md` | New packages, modules, or significant API changes |
| Team directives | All agents | `docs/team-directives.md` | New conventions established during work |
| ADRs | Archie | `docs/adrs/` | Significant architectural decisions |
| Product context | Pat | `docs/product-context.md` | Kickoff Phase 1b, sprint boundaries, human corrections |

## Dependency Management Rules

- Every top-level dependency must have a rationale entry in `dependency-decisions.md`.
- Transitive dependencies are inventoried with their license.
- Run `/pin-versions` to pin versions, regenerate SBOM, and update decisions.
- Copyleft or uncommon licenses in the transitive tree are flagged for review.

## Security & Threat Modeling

Pierrot owns the threat model (`docs/security/threat-model.md`). Created during kickoff Phase 3 (Architecture) with Archie providing data flow diagrams. Uses STRIDE analysis. Updated whenever the attack surface changes. At pre-release, Pierrot verifies the threat model is current.

## Performance Budget

Vik reviews during code review against `docs/performance-budget.md`. Ines verifies at pre-release by running benchmarks and load tests. Created during kickoff if the project has performance-sensitive requirements.

## Test Strategy

Tara owns `docs/test-strategy.md`. Defines what gets tested at which level, coverage targets, and test data strategy. Created during kickoff or first sprint.

## Technical Debt

Grace tracks in `docs/tech-debt.md`. Pat prioritizes debt against feature work at sprint boundaries. Debt that increases risk (security, data integrity, missing tests on critical paths) gets priority. Any debt open for 3+ sprints is escalated to the user.

## Runbooks

Ines owns `docs/runbooks/`. Every alert must have a corresponding runbook. Created alongside the infrastructure they support. Template at `docs/scaffolds/runbook-template.md`.

## Configuration Management

Ines owns `docs/config-manifest.md`. Every environment variable, feature flag, and config file is documented with values per environment. Audited before every deployment.

## Changelog

Diego owns `CHANGELOG.md`. At release time, generate entries from conventional commits, group by type, translate into user-facing language. Breaking changes include migration steps.
