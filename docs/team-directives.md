---
agent-notes: { ctx: "low-ceremony project conventions, positive rules", deps: [CLAUDE.md, docs/process/gotchas.md], state: active, last: "archie@2026-03-21" }
---

# Team Directives

Lightweight conventions the team has settled on. These are **positive rules** — "always X" / "prefer Y over Z" — that don't rise to the level of an ADR but are too important to forget between sessions.

**How this differs from `gotchas.md`:** Gotchas document failure modes and anti-patterns (defensive). Directives document agreed conventions and standards (prescriptive). Gotchas say "don't touch the stove." Directives say "we cook with gas, not electric."

**How this differs from ADRs:** ADRs document significant architectural decisions with context, alternatives, and consequences. Directives are small, low-ceremony rules that accumulate organically. If a directive grows complex enough to need "Alternatives Considered," promote it to an ADR.

## How to Add Directives

Any agent can add a directive to their section during normal work. The format is:

```
- **Directive name.** One-sentence rule. _Why:_ brief rationale.
```

Add directives when:
- The team settles on a convention during code review
- Sato discovers a pattern that should be consistent across the codebase
- Tara establishes a testing convention
- Archie makes a small structural decision that doesn't warrant an ADR
- The human explicitly states a preference

## Code Style (Sato)

<!-- Sato: add coding conventions here as you establish them.
     Examples: "Always use single quotes", "Prefer composition over inheritance",
     "API responses use camelCase", "Error messages include the failing value" -->

## Testing Conventions (Tara)

<!-- Tara: add testing conventions here as you establish them.
     Examples: "Integration tests hit the real database, never mocks",
     "Test names follow given_when_then format",
     "Fixtures go in tests/fixtures/, never inline" -->

## API & Interface Conventions (Archie)

<!-- Archie: add API design conventions here.
     Examples: "All CLI commands support --json output",
     "Config files use TOML, not YAML",
     "Public functions have docstrings, private don't" -->

## Documentation Conventions (Diego)

<!-- Diego: add documentation conventions here.
     Examples: "README quick-start must work in under 5 minutes",
     "Changelog entries use past tense",
     "API docs include a curl example for every endpoint" -->

## Security Conventions (Pierrot)

<!-- Pierrot: add security conventions here.
     Examples: "Never log PII, even at debug level",
     "All user input validated at the boundary",
     "Secrets come from env vars, never config files" -->

## DevOps & Infrastructure (Ines)

<!-- Ines: add infra conventions here.
     Examples: "CI must pass before merge, no exceptions",
     "Docker images use distroless base",
     "All env vars documented in .env.example" -->

## Design & UX (Dani)

<!-- Dani: add design conventions here.
     Examples: "All interactive elements have focus indicators",
     "Error states show recovery actions, not just messages",
     "Color is never the only differentiator" -->
