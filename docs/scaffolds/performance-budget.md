---
agent-notes:
  ctx: "performance thresholds and budget tracking"
  deps: []
  state: stub
  last: "vik@2026-02-15"
  key: ["Vik owns perf review, Ines checks at pre-release"]
---
# Performance Budget

<!-- Vik owns performance review during code review. Ines verifies at pre-release. -->
<!-- Created during kickoff or first sprint. Updated when requirements change. -->

**Project:** [Project Name]
**Last reviewed:** [Date]

## Response Time Targets

| Endpoint / Operation | P50 target | P95 target | P99 target | Current | Status |
|---------------------|------------|------------|------------|---------|--------|
| <!-- e.g. GET /api/users --> | <!-- 50ms --> | <!-- 200ms --> | <!-- 500ms --> | <!-- TBD --> | <!-- TBD --> |

## Resource Budgets

| Metric | Budget | Current | Status |
|--------|--------|---------|--------|
| JS bundle size (gzipped) | | | |
| CSS bundle size (gzipped) | | | |
| Docker image size | | | |
| Memory (RSS, idle) | | | |
| Memory (RSS, peak) | | | |
| Cold start time | | | |
| Database connections (pool) | | | |
| Build time | | | |

## Database Query Budgets

| Query pattern | Max execution time | Max rows scanned | Index required? | Status |
|--------------|-------------------|-----------------|----------------|--------|
| <!-- e.g. user lookup by email --> | <!-- 5ms --> | <!-- 1 --> | <!-- Yes --> | <!-- OK --> |

## Load Targets

| Scenario | Target | Current | Test method |
|----------|--------|---------|-------------|
| Concurrent users | | | |
| Requests/sec (sustained) | | | |
| Requests/sec (burst) | | | |

## Regressions

Track any performance regressions detected:

| Date | What regressed | From | To | Cause | Resolution |
|------|---------------|------|-----|-------|------------|
| | | | | | |

## How to Measure

<!-- Document the tools and methods used to measure performance. -->
<!-- e.g., "Run `npm run bench` for microbenchmarks", "Use k6 for load testing" -->

### Benchmarks
- **Command:** [how to run benchmarks]
- **Environment:** [where to measure — local, staging, etc.]

### Profiling
- **CPU:** [tool and method]
- **Memory:** [tool and method]
- **Bundle analysis:** [tool and method]
