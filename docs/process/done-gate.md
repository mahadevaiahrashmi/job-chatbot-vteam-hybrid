---
agent-notes:
  ctx: "15-item Done Gate checklist for work items"
  deps: [CLAUDE.md]
  state: active
  last: "coordinator@2026-02-28"
---
# Done Gate — Detailed Checklist

This checklist is the quality gate every work item must pass before closing. Referenced by CLAUDE.md § Workflow.

Every work item must pass this gate before closing:

1. **Tests pass** with zero failures.
2. **Typecheck passes** with zero errors. If the project uses a type-checked language, the type checker must pass independently of tests (e.g., Vitest uses esbuild with no type checking, so `tsc` can fail even when tests pass). This catches missing imports, wrong generics, stale type references after migrations, and mock type mismatches.
3. **Formatted** per project's formatter (no diffs).
4. **Linted** with zero warnings.
5. **Code reviewed** — the code-reviewer agent (or at minimum one review lens) has been invoked.
6. **Acceptance criteria met** — the feature works as specified, not just "tests pass."
7. **Docs current** — if the change affects user-facing behavior, Diego has updated docs.
8. **Accessibility reviewed** — if any frontend/UI file was changed, Dani (accessibility lens) has reviewed. Dani must be spawned as a standalone agent, not reviewed inline by the coordinator.
8b. **Visual verification** — if this item changes UI files (`ui/`, `pages/`, `components/`, templates, CSS, layouts), open the affected page(s) in a browser (via Playwright `browser_navigate` + `browser_take_screenshot`, or manual check) and verify they render correctly without console errors. Screenshot evidence is sufficient. This is not a full E2E suite — it's "does it render." _Not applicable to CLIs, libraries, or backend-only services._
9. **Board updated** — status has passed through "In Progress" → "In Review" → "Done" in order (not skipping any). Verify by checking the item's current status on the board (`gh project item-list <NUMBER> --owner <OWNER> --format json`). If "In Review" status doesn't exist on the board, this is a board configuration failure — fix it before proceeding (see `/kickoff` Phase 5 Step 2).
10. **Migration safe** — if schema/data changes are involved, Archie's migration safety checklist passes.
11. **API compatible** — if API contracts changed, backward compatibility verified or new version created.
12. **Tech debt logged** — if shortcuts were taken, they're recorded in `docs/tech-debt.md`.
12b. **Directives updated** — if a new convention was established or discovered during this work, add it to `docs/team-directives.md`.
13. **SBOM current** — if dependencies were added/removed/upgraded, Pierrot has updated the SBOM.
14. **Operational baseline checked** — if this work item changes application behavior (not docs-only, not CI-only), verify it hasn't degraded the operational baseline (`docs/process/operational-baseline.md`):
    - Logging: new code paths log at appropriate levels.
    - Error patterns: new error handling follows the project's established pattern.
    - Config: any new config values are documented and validated.
    - README: if user-facing behavior changed, the quick-start is still accurate.
15. **External integration smoke-tested** — if this work item integrates with external tools, services, or binaries (subprocess spawning, external APIs, CLI tool invocation), the happy path has been verified against the real tool, not just mocks. Mocked unit tests verify internal logic; this gate verifies the integration actually works end-to-end. If the external tool is unavailable in CI, document which manual verification was performed and by whom.
