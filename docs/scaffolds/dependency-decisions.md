---
agent-notes:
  ctx: "dependency rationale and transitive dep inventory"
  deps: [docs/scaffolds/sbom.md]
  state: stub
  last: "pierrot@2026-02-15"
---
# Dependency Decisions

<!-- This file explains WHY each dependency exists. Maintained by Pierrot. -->
<!-- Every top-level dependency must have an entry here before it's accepted. -->

## Top-Level Dependencies

For each dependency we've explicitly chosen, document the rationale.

### [Package Name]

- **Package:** `package-name`
- **Version:** `x.y.z`
- **License:** MIT
- **Why we're using it:** [Explain the problem it solves, why this package over alternatives, and any trade-offs accepted.]
- **Alternatives considered:** [What else was evaluated and why it was rejected.]
- **Added:** [Date] by [Agent/Human]

<!-- Copy the template above for each top-level dependency. -->

---

## Transitive Dependencies

These are dependencies we pull in indirectly — we didn't choose them, but they're in our dependency tree because of packages we did choose. This table is regenerated whenever dependencies change (see `/pin-versions`).

| Package | Version | License | Pulled in by |
|---------|---------|---------|--------------|
| <!-- e.g. ms --> | <!-- 2.1.3 --> | <!-- MIT --> | <!-- express → debug → ms --> |

### License Flags

Any transitive dependency with a **copyleft license** (GPL, LGPL, AGPL, MPL) or an **uncommon/unknown license** is flagged here for Pierrot's review:

| Package | License | Pulled in by | Risk assessment |
|---------|---------|--------------|-----------------|
| <!-- populated during audits --> | | | |
