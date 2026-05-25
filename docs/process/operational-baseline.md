---
agent-notes:
  ctx: "cross-cutting operational concerns checklist"
  deps: [CLAUDE.md, docs/process/done-gate.md, docs/process/team-governance.md]
  state: active
  last: "coordinator@2026-02-28"
---
# Operational Baseline

## The Structural Problem

The methodology tracks work **vertically** — feature by feature, each with its own tests, review, and Done Gate. But some concerns cut **horizontally** across all features: logging, error UX, configuration, documentation accuracy. These concerns share five failure modes:

1. **No work item owns it** — they are product properties, not features.
2. **Per-item Done Gate can't see it** — each item passes while the product degrades.
3. **Sprint boundary audits process health, not product health** — board compliance, debates, status flow — never "does the product actually work?"
4. **Scaffolds don't seed the patterns** — if not established on day 1, they develop inconsistently.
5. **Relevant persona is absent, optional, or walled off from app code** — Ines can't review app code, Diego is passive, Debra is optional.

This document closes the gap by distributing responsibility across existing agents and integration points.

## The 11 Operational Concerns

### 1. Observability / Logging

| Attribute | Value |
|-----------|-------|
| **Description** | Application produces structured, leveled logs that make failures diagnosable without a debugger attached. |
| **Review owner** | Ines (operational review lens) |
| **Implementation owner** | Sato |
| **Seeded by** | Scaffold command (logging module + `--verbose`/`--debug` flags) |
| **Verified at** | Code review (per-diff), sprint boundary (audit), pre-release (full) |
| **Minimum viable bar** | Logging library configured, WARNING default level, `--verbose` (INFO) and `--debug` (DEBUG) flags wired, significant operations logged at INFO, errors logged with context. |

### 2. Error UX Consistency

| Attribute | Value |
|-----------|-------|
| **Description** | Users see consistent, actionable error messages. Internal errors and user-facing errors are distinct types. |
| **Review owner** | Ines (operational review lens) |
| **Implementation owner** | Sato |
| **Seeded by** | Scaffold command (error module with user-facing vs. internal error shapes) |
| **Verified at** | Code review (per-diff), sprint boundary (audit) |
| **Minimum viable bar** | Error module exists, user-facing errors include what happened + what to do, internal errors are caught at top level and shown as generic messages with a debug-level stack trace. |

### 3. CLI Behavioral Contract

| Attribute | Value |
|-----------|-------|
| **Description** | The CLI behaves predictably: defined exit codes, `--help` on every command, consistent flag naming, stdout for output, stderr for diagnostics. |
| **Review owner** | Ines (operational review lens) |
| **Implementation owner** | Sato |
| **Seeded by** | Scaffold command (exit code constants, top-level handler) |
| **Verified at** | Code review (per-diff), sprint boundary (audit) |
| **Minimum viable bar** | Exit codes: 0=success, 1=user error, 2=internal error. `--help` works. Output goes to stdout, diagnostics to stderr. |

### 4. Configuration UX

| Attribute | Value |
|-----------|-------|
| **Description** | Configuration is validated at startup with clear error messages. Precedence is documented. `.env.example` (or equivalent) is accurate. |
| **Review owner** | Ines (operational review lens) |
| **Implementation owner** | Sato |
| **Seeded by** | Scaffold command (config module with validation) |
| **Verified at** | Code review (per-diff), sprint boundary (audit) |
| **Minimum viable bar** | Config validation at boundaries with actionable messages ("Missing API_KEY — set it in .env or pass --api-key"), `.env.example` matches actual config, precedence documented in README or config module comment. |

### 5. Graceful Degradation

| Attribute | Value |
|-----------|-------|
| **Description** | When external dependencies (APIs, databases, services) are unavailable, the application fails clearly rather than hanging or producing cryptic errors. |
| **Review owner** | Ines (operational review lens) |
| **Implementation owner** | Sato |
| **Seeded by** | Architecture phase (failure mode analysis) |
| **Verified at** | Code review (per-diff), sprint boundary (audit), pre-release (chaos lens) |
| **Minimum viable bar** | External calls have timeouts, timeout errors produce user-facing messages, the application does not hang on unreachable services. |

### 6. Documentation Bit-Rot

| Attribute | Value |
|-----------|-------|
| **Description** | README quick-start is literally runnable. Documentation reflects current behavior, not aspirational behavior. |
| **Review owner** | Diego |
| **Implementation owner** | Diego |
| **Seeded by** | Scaffold command (runnable quick-start) |
| **Verified at** | Sprint boundary (Diego "5-minute test"), pre-release (full) |
| **Minimum viable bar** | A new user can clone the repo and follow the README quick-start to a working state without undocumented steps. Broken quick-start is a P1 defect. |

### 7. Performance Budget Population

| Attribute | Value |
|-----------|-------|
| **Description** | If a performance budget exists, it has measured values — not just targets. |
| **Review owner** | Vik (review) / Ines (verify) |
| **Implementation owner** | Ines |
| **Seeded by** | Kickoff Phase 3 (if performance-sensitive) |
| **Verified at** | Sprint boundary (periodic), pre-release (mandatory) |
| **Minimum viable bar** | Budget has both "Target" and "Current" columns. "Current" is populated with measured values, not "TBD." |

### 8. Error Handling Pattern Consistency

| Attribute | Value |
|-----------|-------|
| **Description** | The codebase follows one error handling pattern, not a different approach per file or module. |
| **Review owner** | Ines (operational review lens) |
| **Implementation owner** | Sato |
| **Seeded by** | Scaffold command (error module establishes the pattern) |
| **Verified at** | Code review (per-diff), sprint boundary (audit) |
| **Minimum viable bar** | One error handling pattern documented or established by the error module. New code follows it. Code review flags deviations. |

### 9. Idempotency

| Attribute | Value |
|-----------|-------|
| **Description** | Commands and operations that could reasonably be retried are safe to retry. State-modifying operations either check preconditions or are naturally idempotent. |
| **Review owner** | Ines (operational review lens) |
| **Implementation owner** | Sato |
| **Seeded by** | Architecture phase (Archie identifies retry-sensitive operations) |
| **Verified at** | Code review (per-diff, when relevant), pre-release (audit) |
| **Minimum viable bar** | State-modifying operations are aware of retry scenarios. "Create" operations check for existing state. Documented which operations are safe to retry. |

### 10. i18n Readiness

| Attribute | Value |
|-----------|-------|
| **Description** | User-facing strings are externalizable — not hardcoded into business logic — even if only one locale is supported initially. |
| **Review owner** | Ines (operational review lens) |
| **Implementation owner** | Sato |
| **Seeded by** | Architecture phase (if multi-locale is a known requirement) |
| **Verified at** | Pre-release (audit, if applicable) |
| **Minimum viable bar** | User-facing strings are in one findable location (not scattered across business logic). Full i18n framework is NOT required — just separation of strings from logic. Only applicable if the project targets multiple locales or is a library. |

### 11. External Process Spawn Safety

| Attribute | Value |
|-----------|-------|
| **Description** | Subprocesses are spawned with explicitly configured stdio channels, timeouts, signal handling, and cleanup. No reliance on library defaults for stdin/stdout/stderr. |
| **Review owner** | Ines (operational review lens) |
| **Implementation owner** | Sato |
| **Seeded by** | Architecture phase (when external tool integration is identified) |
| **Verified at** | Code review (per-diff), sprint boundary (audit), Done Gate #15 |
| **Minimum viable bar** | All subprocess spawn calls explicitly set stdin, stdout, stderr. Timeouts are configured. Integration tests exist that spawn the real binary (gated behind env var). |

## Applicability Matrix

Not every concern applies to every project type. Use this matrix to scope the baseline.

| Concern | CLI | Web App | AI Tool | Static Site |
|---------|:---:|:-------:|:-------:|:-----------:|
| Observability / Logging | **Yes** | **Yes** | **Yes** | No |
| Error UX Consistency | **Yes** | **Yes** | **Yes** | Minimal |
| CLI Behavioral Contract | **Yes** | No | Partial | No |
| Configuration UX | **Yes** | **Yes** | **Yes** | Minimal |
| Graceful Degradation | **Yes** | **Yes** | **Yes** | No |
| Documentation Bit-Rot | **Yes** | **Yes** | **Yes** | **Yes** |
| Performance Budget Population | Situational | **Yes** | Situational | **Yes** |
| Error Handling Consistency | **Yes** | **Yes** | **Yes** | No |
| Idempotency | Situational | **Yes** | Situational | No |
| i18n Readiness | Situational | Situational | Situational | Situational |
| External Process Spawn Safety | **Yes** | Situational | **Yes** | No |
| Visual Smoke Test | No | **Yes** | Situational | **Yes** |

**Legend:** **Yes** = always checked. Partial = subset applies. Situational = check if the project has relevant requirements. Minimal = lightweight version applies. No = skip.

## Maturity Model

### Foundation (Sprint 1)

Established by the scaffold command and first sprint. The minimum to avoid embedding bad habits:

- Logging module configured with level control
- Error module with user-facing vs. internal distinction
- Config validation at startup with clear messages
- README quick-start is literally runnable
- Exit codes defined (CLI projects)

### Production (Pre-Release)

Required before shipping to users:

- All applicable concerns at minimum viable bar
- Performance budget populated with measured values
- Graceful degradation for all external dependencies
- Error patterns consistent across the codebase
- Documentation matches actual behavior

### Excellence (Ongoing)

Aspirational; checked periodically but not gating:

- Structured logging with correlation IDs
- Error telemetry and categorization
- Config hot-reload where applicable
- Automated documentation accuracy checks
- Full i18n support (if multi-locale)

## Sprint Cadence

| Check frequency | Concerns |
|----------------|----------|
| **Per code review** | Logging coverage, error pattern consistency, config documentation, debug flag support, subprocess stdio configuration (lightweight — Ines situational lens on diffs that touch app behavior) |
| **Per sprint boundary** | All 12 concerns audited by Ines + Diego README test (Step 5b). Visual smoke test by Dani + Playwright (Step 5c, web apps only). Full audit, not just diffs. |
| **Per release** | All applicable concerns at Production maturity or above. Diego runs full documentation accuracy pass. Ines runs graceful degradation and config audit. |
