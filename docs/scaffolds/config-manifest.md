---
agent-notes:
  ctx: "config manifest, env vars, feature flags per environment"
  deps: []
  state: stub
  last: "ines@2026-02-15"
  key: ["Ines owns, audited at pre-release"]
---
# Configuration Manifest

<!-- Ines owns this document. Audited before every release/deployment. -->
<!-- If a config value isn't documented here, it shouldn't exist. -->

**Project:** [Project Name]
**Last audited:** [Date]

## Environment Variables

| Variable | Required? | Default | Dev | Staging | Prod | Description |
|----------|-----------|---------|-----|---------|------|-------------|
| <!-- e.g. DATABASE_URL --> | <!-- Yes --> | <!-- none --> | <!-- postgres://localhost/dev --> | <!-- [vault] --> | <!-- [vault] --> | <!-- Primary database connection string --> |

### Secret Variables

Variables that contain sensitive values. **Never commit these.** Values should come from a secrets manager.

| Variable | Source | Rotation policy | Last rotated |
|----------|--------|----------------|-------------|
| <!-- e.g. API_SECRET --> | <!-- AWS Secrets Manager --> | <!-- 90 days --> | <!-- [date] --> |

## Feature Flags

| Flag | Type | Dev | Staging | Prod | Description | Owner |
|------|------|-----|---------|------|-------------|-------|
| <!-- e.g. ENABLE_NEW_CHECKOUT --> | <!-- boolean --> | <!-- true --> | <!-- true --> | <!-- false --> | <!-- New checkout flow --> | <!-- Pat --> |

## Configuration Files

| File | Environment-specific? | Description |
|------|--------------------|-------------|
| <!-- e.g. config/database.yml --> | <!-- Yes (per-env sections) --> | <!-- Database configuration --> |

## Drift Detection

How to verify configuration is consistent across environments:

- **Command:** [e.g., `scripts/check-config.sh`]
- **CI check:** [Yes/No — is config drift checked in CI?]
- **Last audit findings:** [any issues found]

## Adding a New Config Value

1. Add the variable to this manifest first.
2. Set values for all environments (or mark as N/A).
3. If secret: add to the secrets manager, document the source and rotation policy.
4. If feature flag: assign an owner (usually Pat).
5. Update the application code to read it.
6. Update `.env.example` or equivalent.
