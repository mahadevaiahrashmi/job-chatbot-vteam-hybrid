---
agent-notes:
  ctx: "test strategy, pyramid, coverage targets"
  deps: []
  state: stub
  last: "tara@2026-02-28"
  key: ["Tara owns, created during kickoff or sprint 1"]
---
# Test Strategy

<!-- Tara owns this document. Created during kickoff or first sprint. -->
<!-- Tara references this when writing tests to ensure consistent coverage. -->

**Project:** [Project Name]
**Last reviewed:** [Date]

## Testing Principles

1. **Test behavior, not implementation.** Tests verify what the system does, not how it does it.
2. **The test pyramid is law.** Many unit tests, fewer integration tests, minimal e2e tests.
3. **Every bug gets a regression test.** Before fixing a bug, write a test that reproduces it.
4. **Tests are documentation.** Test names describe system behavior. A new developer should understand the system by reading the tests.

## Test Pyramid

### Unit Tests
- **Scope:** Individual functions, methods, components in isolation.
- **Coverage target:** [e.g., 80%+ line coverage on business logic]
- **Framework:** [e.g., vitest, pytest, cargo test]
- **Run command:** [e.g., `npm test`]
- **Speed target:** Full suite < [e.g., 30 seconds]

### Integration Tests
- **Scope:** Component interactions, database queries, API endpoints.
- **Coverage target:** [e.g., all API endpoints, all DB queries]
- **Framework:** [e.g., supertest, pytest with fixtures]
- **Run command:** [e.g., `npm run test:integration`]
- **Dependencies:** [e.g., test database, Docker]

### End-to-End Tests
- **Scope:** Critical user flows only.
- **Coverage target:** [e.g., login, core workflow, payment]
- **Framework:** [e.g., Playwright, Cypress]
- **Run command:** [e.g., `npm run test:e2e`]
- **Flaky test policy:** [e.g., quarantine after 2 flakes, fix within 1 sprint]

## What Gets Tested Where

| Area | Unit | Integration | E2E | Notes |
|------|------|-------------|-----|-------|
| Business logic | Yes | — | — | Pure functions, no I/O mocking needed |
| API endpoints | — | Yes | — | Request/response validation |
| Database queries | — | Yes | — | Against test DB with realistic data |
| Auth flows | Yes (logic) | Yes (middleware) | Yes (full flow) | Critical path, all levels |
| UI components | Yes (render) | — | — | Component tests, not DOM tests |
| Critical user flows | — | — | Yes | Only the flows that, if broken, are P0 |
| Error handling | Yes | Yes | — | Unhappy paths at unit + integration |
| External process invocation | — | Yes | — | Real binary smoke test gated behind env var; verifies spawn options, stdio config, and exit lifecycle |
| Config/env loading | Yes | — | — | Validate all config shapes |

## What Is NOT Tested (and why)

<!-- Explicitly document what's excluded and the rationale. -->
| Area | Reason |
|------|--------|
| <!-- e.g. third-party API responses --> | <!-- Mocked at integration level; vendor's responsibility --> |

## Coverage Gates

| Scope | Metric | Threshold | Enforced by |
|-------|--------|-----------|-------------|
| Overall | Line coverage | [e.g., 80%] | CI |
| New code | Line coverage | [e.g., 90%] | Code review (Tara) |
| Critical paths | Branch coverage | [e.g., 95%] | Code review (Tara) |

## Test Data Strategy

- **Factories/fixtures:** [approach for generating test data]
- **Database seeding:** [approach for integration tests]
- **PII in tests:** Never use real user data. Use faker/factory libraries.
- **Snapshot testing:** Use sparingly. Only for stable output formats (e.g., serialized API responses). Review diffs carefully.
