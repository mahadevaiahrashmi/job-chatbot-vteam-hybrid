---
agent-notes:
  ctx: "software bill of materials, all dependencies"
  deps: [docs/scaffolds/dependency-decisions.md]
  state: stub
  last: "pierrot@2026-02-15"
---
# Software Bill of Materials (SBOM)

<!-- This file is maintained by Pierrot. Update it whenever dependencies change. -->
<!-- Sato must notify Pierrot after adding, removing, or upgrading any dependency. -->

**Project:** [Project Name]
**Last updated:** [Date]
**Package manager:** [npm / pip / cargo / etc.]
**Lock file:** [package-lock.json / requirements.txt / Cargo.lock / etc.]

## Direct Dependencies

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| <!-- e.g. express --> | <!-- 4.18.2 --> | <!-- MIT --> | <!-- HTTP server framework --> |

## Dev Dependencies

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| <!-- e.g. vitest --> | <!-- 1.6.0 --> | <!-- MIT --> | <!-- Test runner --> |

## Transitive Dependencies

See the full transitive dependency tree in [dependency-decisions.md](dependency-decisions.md#transitive-dependencies).

**Total dependency count:** [N direct + M transitive = T total]

## License Summary

| License | Count | Notes |
|---------|-------|-------|
| MIT | | |
| Apache-2.0 | | |
| ISC | | |
| BSD-2-Clause | | |
| BSD-3-Clause | | |
| Other | | Flag any GPL, AGPL, or uncommon licenses for Pierrot review |

## Known Vulnerabilities

| Package | CVE | Severity | Status | Notes |
|---------|-----|----------|--------|-------|
| <!-- populated during audits --> | | | | |
