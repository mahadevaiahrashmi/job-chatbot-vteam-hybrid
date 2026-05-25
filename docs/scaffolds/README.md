---
agent-notes: { ctx: "explains scaffold stubs, deployed to final paths during setup", deps: [CLAUDE.md], state: canonical, last: "diego@2026-03-11" }
---

# Project Scaffolds

These are **stub files** that get moved to `docs/` during scaffolding or kickoff. They are templates for project-specific documentation — fill them in as your project takes shape.

| File | Deploys to | Owner |
|------|-----------|-------|
| `code-map.md` | `docs/code-map.md` | Coordinator |
| `config-manifest.md` | `docs/config-manifest.md` | Ines |
| `performance-budget.md` | `docs/performance-budget.md` | Vik (review), Ines (verify) |
| `tech-debt.md` | `docs/tech-debt.md` | Grace (tracks), Pat (prioritizes) |
| `test-strategy.md` | `docs/test-strategy.md` | Tara |
| `sbom.md` | `docs/sbom/sbom.md` | Pierrot |
| `dependency-decisions.md` | `docs/sbom/dependency-decisions.md` | Pierrot |
| `threat-model.md` | `docs/security/threat-model.md` | Pierrot (owns), Archie (DFDs) |
| `runbook-template.md` | `docs/runbooks/template.md` | Ines |

**Scaffold commands** (`/scaffold-*`) and `/kickoff` move these files into `docs/` automatically.
