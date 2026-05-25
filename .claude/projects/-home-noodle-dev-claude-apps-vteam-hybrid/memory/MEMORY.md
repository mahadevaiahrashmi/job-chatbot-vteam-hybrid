# Auto Memory

## #1 — Session Entry Protocol (from 2026-02-20 retro)

**Anti-pattern: Plan-as-Bypass.** When a detailed plan exists (from plan mode, prior session, or human spec), do NOT treat it as pre-approved. The plan is INPUT to the process, not a bypass of it.

Before writing any code — including types, tests, or ADRs — answer:
1. **Do GitHub issues exist for this work?** If no → create them (Pat + Grace).
2. **Does this work involve an architectural decision?** If yes → Architecture Gate (Archie + Wei as standalone agents).
3. **Am I about to write implementation code?** If yes → Tara writes tests first.

**Detection signal:** If my first tool call is `Read` on a source file (not `docs/code-map.md`, governance docs, or sprint plan), I'm likely in bypass mode.

## Key Process Reminders

- Plans don't replace process. Still need: GitHub issues, architecture gate, TDD, code review, Done Gate.
- Wei must be invoked as a standalone agent for architecture debates — coordinator analysis is not a substitute.
- Board transitions are mandatory and ordered: Backlog → Ready → In Progress → In Review → Done.
- Code review (Vik + Tara + Pierrot) happens BEFORE committing, not after.
