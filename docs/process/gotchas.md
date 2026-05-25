---
agent-notes:
  ctx: "implementation gotchas and established patterns"
  deps: [CLAUDE.md]
  state: active
  last: "coordinator@2026-03-28"
---
# Known Patterns and Gotchas

Extracted from CLAUDE.md to reduce context window load. Read this when working on implementation or debugging tasks. Projects populate sections as they discover gotchas.

## Testing Patterns (Tara)

- **Assert content, not just existence.** A check like "a Bold run exists" can false-positive if an unrelated element happens to match. Always assert the **text content** inside the matched element, not just its presence or formatting. **Detection signal:** test asserts `toBeTruthy()` or `toHaveLength(1)` on a query result without checking what's inside. **Fix:** add content assertions alongside structural assertions — e.g., assert both "element is bold" and "element text is 'Expected Value'."

- **Test real-world combinations, not just individual features.** Synthetic test data that exercises features in isolation (bold text, then a table, then a link) misses bugs that only appear in realistic combinations (bold links inside table cells, strikethrough in nested lists). **Detection signal:** all tests pass on synthetic data but break on real user input. **Fix:** add at least one test that processes a representative real-world sample alongside feature-specific unit tests.

<!-- Tara: add project-specific testing gotchas here as you discover them.
     Examples: mocking strategies that work/fail, flaky test patterns,
     edge cases that keep recurring, test setup quirks. -->

## Code Review Findings (Vik)

<!-- Vik: add recurring code smells, complexity hotspots, and accepted
     trade-offs here. Tracking these avoids redundant flagging across sessions. -->

## Security & Compliance (Pierrot)

<!-- Pierrot: add accepted risks, threat surfaces evaluated, and security
     trade-offs here. Decisions the human explicitly approved should be recorded
     so they aren't re-flagged in future sessions. -->

## Implementation Patterns (Sato)

- **Sweep all case variants when renaming.** `replace_all` for `marketId` misses `MarketId`, `market_id`, `MARKET_ID`, and names like `validateMarketId`. After any rename, run a case-insensitive grep as a final sweep: `grep -riE 'oldname|old_name'` across the repo. Check function names, type names, variable names, and comments.

<!-- Sato: add codebase-specific implementation patterns, performance learnings,
     and quirks here. Examples: which abstractions work well, fragile areas,
     API client behaviors that differ from their types. -->

## Architecture Patterns (Archie)

- **YAGNI vs. Planned Capabilities (the Drift Trap).** YAGNI says don't build abstractions for hypothetical futures. But when a future capability is architecturally planned (has an ADR, appears in the architecture doc, is on the roadmap), the abstraction boundary that enables it is a **current requirement**, not speculation. Using consumer-specific concepts in a shared type because "we only support X today" is not YAGNI — it's tech debt against a planned capability. **Detection signal:** a shared/core type contains concepts specific to one consumer while the architecture plans for multiple consumers. **Fix:** use format-neutral representations in shared types; consumer-specific conversions happen at the boundary (in the consumer, not in Core).

<!-- Archie: add additional architectural constraints, integration point knowledge, and
     schema evolution notes here. Patterns that informed past ADRs but aren't
     worth a standalone ADR themselves. -->

## Adapter / Integration Gotchas

- **execa v9 `stdin: 'pipe'` default hangs subprocesses.** execa v9 changed `stdin` from `'inherit'` to `'pipe'`. CLI tools that check stdin connectivity (e.g., `claude -p`, `gemini`) see a connected pipe and wait for EOF, which never comes — the subprocess hangs until timeout. **Detection signal:** subprocess calls work with `--version` or `--help` (which exit immediately) but hang with actual workload flags. **Fix:** always set `stdin: 'ignore'` unless you explicitly need to write to the subprocess's stdin. Audit all execa/child_process calls to explicitly configure all three stdio channels. ⚠️ *Volatile — verified 2026-03-30, CLI 2.1.87. See `docs/research/claude-cli-invocation-patterns.md` Pattern 1.*

- **Health checks that don't exercise the real code path.** A health check like `tool --version` exits immediately without reading stdin, so it succeeds even when the actual call (`tool -p "prompt"`) would hang. **Detection signal:** health check passes but actual tool invocation fails/hangs. **Fix:** health checks should exercise the same flags and stdio configuration as the real invocation, just with minimal input.

- **LLMs wrap JSON in markdown fences.** Even with "respond with valid JSON only" in the prompt, models frequently wrap responses in ` ```json ... ``` ` fences. Parsing the raw response as JSON fails. **Detection signal:** `JSON.parse()` / `json.loads()` throws on LLM output that looks correct when printed. **Fix:** always strip markdown fences from LLM output before parsing. Use a utility like `extractJson()` that handles fenced and unfenced responses. ⚠️ *Volatile — verified 2026-03-30. See `docs/research/claude-cli-invocation-patterns.md` Pattern 3 for a robust extraction function.*

- **Strip `CLAUDECODE` env var when spawning claude subprocesses.** Claude Code CLI sets `CLAUDECODE=1` in the environment. Spawned `claude --print` processes check for this variable and refuse to run (to prevent recursive spawning). **Detection signal:** subprocess exits immediately with an error about nested invocation. **Fix:** strip the variable before spawning: `delete env.CLAUDECODE` (JS) or `env.pop('CLAUDECODE', None)` (Python). Also strip `ANTHROPIC_API_KEY` if you want the subprocess to use subscription auth instead of per-token billing. ⚠️ *Volatile — verified 2026-03-30, CLI 2.1.87. See `docs/research/claude-cli-invocation-patterns.md` Pattern 5.*

- **Claude CLI invocation has 8 known patterns — read the research doc first.** Two projects independently discovered the same set of patterns for spawning `claude --print` as a subprocess: prompt via `-p` flag (not stdin), no `--bare`/`--output-format json`, extract JSON from plain text, explicit `--model`, env var stripping, input validation, stderr sanitization, and settle guard for timeouts. If your project spawns `claude` as a subprocess, read `docs/research/claude-cli-invocation-patterns.md` before writing any adapter code. ⚠️ *Volatile — verified 2026-03-30, CLI 2.1.87. The Claude CLI is actively evolving; verify each pattern against `claude --help` and current release notes before adopting. Update the research doc's "Reviewed" date after verification.*

## Build and Run

<!-- Add build, bundling, and runtime gotchas here -->

## Process

- **Plans don't replace process (Plan-as-Bypass anti-pattern).** A detailed implementation plan (from plan mode, a prior session, or a human-provided spec) is **input** to the V-Team phases, not a bypass. The plan still needs: GitHub issues (Grace), architecture gate if applicable (Archie + Wei as standalone agents), TDD (Tara → Sato), code review (Vik + Tara + Pierrot), and Done Gate. **Detection signal:** if the coordinator's first tool call is `Read` on a source file (not `docs/code-map.md`, governance docs, or the sprint plan), it's likely in bypass mode. See `2026-02-20-process-violation-plan-bypass.md` for the full retro.

- **Wei must be invoked as a standalone agent.** The coordinator's own analysis of trade-offs is not a substitute for invoking Wei as a standalone agent during architecture debates. If an ADR claims "Wei debate resolved" but no Wei agent was spawned, the gate has not passed.

- **Quick-Test Bypass anti-pattern.** The coordinator writes tests directly "to save time" instead of invoking Tara. The tests look reasonable but miss text content assertions, edge cases, and structural invariants. They become the committed suite and the gaps become permanent. **Detection signal:** test code appears in the coordinator's response with no Tara agent invocation. **Fix:** always invoke Tara for test authoring. Even for exploratory/diagnostic tests, hand them to Tara for review before committing. See `docs/process/team-governance.md` § Quick-Test Bypass for the full pattern.

- **"Invoke the team" means spawn subagents (Solo-Coordinator anti-pattern).** When the human uses language like "invoke the team", "use the team", "have Cam look at this", or names any persona, the coordinator MUST spawn those agents via the Task tool. The coordinator doing the work inline — even if the output is good — violates the explicit human request. **Detection signal:** the human asked for a named persona or "the team" but no Task tool calls with `subagent_type` matching a persona appear in the response. **Fix:** parse the request for persona names or team-level language, then spawn the appropriate agents before doing any work.

- **Use scripts for stable logic, commands for evolving knowledge.** Static scripts are ideal when the rules are well-defined and unlikely to change. But when automation requires understanding things that change externally — evolving formats, shifting best practices, new API conventions — prefer a Claude Code command over a script. Commands bring current understanding (and can web-search) on every run.

- **Proxy mode is conservative, not permissive.** When the human is unavailable and Pat is acting as proxy, Pat defaults to the safer, more reversible option. The guardrails are strict:

  | Pat CAN (proxy) | Pat CANNOT (proxy) |
  |-----------------|-------------------|
  | Prioritize backlog items | Approve or reject ADRs |
  | Accept features against existing criteria | Change project scope |
  | Answer questions covered by product-context.md | Make architectural choices |
  | Defer items to next sprint | Merge to main |
  | Apply conservative defaults | Override Pierrot or Tara vetoes |

  When a question falls outside proxy authority, it blocks until the human returns. All proxy decisions are logged in `.claude/handoff.md` under `## Proxy Decisions (Review Required)`.

- **Product-context is a hypothesis, not ground truth.** `docs/product-context.md` captures Pat's model of the human's product philosophy — it's an educated guess that improves over time. The human can correct it at any time. When the human overrides a product-context-based recommendation, Pat updates the doc and logs the correction in the Correction Log table. Don't treat product-context entries as immutable rules.

- **Phase 1b must precede acceptance criteria writing.** Pat's Human Model Elicitation (kickoff Phase 1b) must complete before Pat writes acceptance criteria (Phase 4). The product context informs what "done" means to this human. Skipping 1b means acceptance criteria are written without understanding the human's quality bar, scope appetite, or non-negotiables.

- **Verify GitHub access before board operations.** Any workflow that touches the project board (sprint-boundary, kickoff, resume, handoff) must verify `gh auth status` and board accessibility before attempting board operations. If `gh` commands fail, STOP and ask the user to fix it — don't proceed and fail mid-workflow. The pre-flight checks are in: sprint-boundary Step 0, kickoff Phase 5 Pre-Flight, resume Step 3, and handoff Step 1. The resume check is especially critical — without it, a full sprint runs board-blind and every status transition is silently skipped.

- **Check devcontainer before implementation.** After planning completes (either via `/plan` or `/kickoff` Phase 5), check whether `.devcontainer/` exists. If not, ask the user if they want one before starting implementation. This prevents environment inconsistency issues during TDD cycles.

- **Precedent-Blindness anti-pattern (False Architecture Dilemma).** The coordinator encounters a capability that needs to be added (e.g., "new module needs to read config files") and treats it as a novel architectural decision requiring human review — when the existing codebase already has an established pattern for the same problem (e.g., another module already reads config via a shared utility). **Detection signal:** the coordinator flags an "architecture decision" or "proxy decision" for something another module already does. The handoff says "deferred — needs architectural review" for a problem with a working solution in `src/`. **Fix:** before flagging a blocking decision, check whether another module/package already handles the same concern. If yes, follow that pattern — it's a precedent, not a decision. Only flag genuinely novel choices where no existing pattern applies.

- **Run `/handoff` after completing each wave.** When a session completes a wave but not the full sprint, run `/handoff` before ending the session. A stale handoff forces the next session to reconstruct state from git history, which is slower and error-prone.

- **Agents own their gotchas sections.** The agent-attributed sections at the top of this file (Testing Patterns → Tara, Code Review Findings → Vik, etc.) are written by the named agent at the end of their work, as part of the done gate or handoff. Record project-specific operational knowledge that would save time in a future session — not general programming knowledge, not things already in ADRs or `code-map.md`. Keep entries specific: "mock the gateway at HTTP level, not SDK level, because the SDK swallows retry errors" beats "be careful with mocking." If an entry becomes broadly relevant beyond its section, promote it to an ADR, `code-map.md`, or the template itself.

- **Sprint boundary must end with a clean-tree gate.** Multi-step workflows (sprint boundary, kickoff) involve many file operations — archival moves, artifact creation, code reviews. Commits that run partway through the workflow leave late-written files unstaged. The `/sprint-boundary` Step 8 enforces a terminal `git status --porcelain` check and stages any orphaned changes. If you're writing a similar multi-step workflow, end it with the same pattern: check, stage, commit, re-check.

- **Diagnostic Blindness anti-pattern.** When a testing or debugging gap is identified, the team designs solutions from scratch (install LibreOffice for visual testing, build a custom comparator, add a new dependency) without checking whether a planned backlog item already solves the problem. A "preview" feature planned for sprint 8 is exactly the visual test oracle you need in sprint 3 — but because Tara thinks about test infrastructure and Pat thinks about feature priority in separate loops, neither connects the dots. **Detection signal:** Tara proposes heavyweight test infrastructure for visual/output verification while a rendering, preview, or export feature sits in the backlog. Sato designs a debugging approach that duplicates a planned observability feature. **Fix:** (1) Tara scans the backlog during test design for features that could serve as test oracles or diagnostic tools — see Tara's "Backlog-Aware Test Design" section. (2) Pat applies "dual-duty prioritization" — items that serve both user-facing and internal purposes get a priority boost and are candidates for pull-forward. (3) During sprint planning, the coordinator asks: "Does any backlog item enable better testing or diagnostics for what we've already built?" See `docs/process/team-governance.md` § Sprint Planning Integration.

- **Invisible UI anti-pattern (post-mortem: portfolio-manager Sprint 1-3).** Three sprints of web UI code shipped without anyone opening a browser. Tests passed, type checks passed, code review passed, operational baseline audit passed. Every gate was green — but the gates are all code-centric. The team had Playwright available and Dani in the roster, but no gate triggered either. **Root cause:** Done Gate #6 ("acceptance criteria met") was interpreted as "tests pass" rather than "I can see it working." Done Gate #8 (Dani reviews UI changes) was never enforced because it's a roster rule, not a workflow step. Diego's 5-minute test verified the server starts but never opened the URL. **Detection signal:** the project has a UI, Playwright is available, and Dani is in the agent roster — but `browser_navigate` has never been called and no Dani agent has been spawned. If you reach Sprint 2 of a web project and browser-based verification hasn't happened, this anti-pattern is active. **Fix:** Done Gate #8b (visual verification for UI changes), Sprint Boundary Step 5c (Playwright smoke test), and enforce Dani invocation as a workflow step, not a roster annotation. See `docs/process/done-gate.md` and `/sprint-boundary`.

- **Horizontal Blindness anti-pattern.** Cross-cutting concerns (logging, error UX, config, debug support, README accuracy) fall between vertical work items. No single item owns them, so they degrade silently. **Detection signal:** 3+ sprints in with no logging or debug flags, README quick-start is broken, error messages are inconsistent across modules. **Fix:** run the operational baseline audit (`docs/process/operational-baseline.md`). Done Gate #14 catches per-item regressions; sprint boundary Step 5b catches product-level drift.

- **Green-Bar-Red-Product anti-pattern.** Every Done Gate passes individually, but the product isn't shippable — no observability, broken quick-start, inconsistent errors. The per-item gate verifies each item in isolation; it cannot see product-level properties that emerge from the combination. **Detection signal:** all items pass Done Gate, but a new user can't get the product working from the README, or production failures produce no useful diagnostics. **Fix:** Done Gate #14 provides per-item defense; sprint boundary Step 5b provides product-level defense. Both reference `docs/process/operational-baseline.md`.

- **Code-reviewer subagent sometimes fails to persist output.** The code-reviewer subagent occasionally completes its analysis but fails to write the review document to disk. After invoking code-reviewer, always verify the expected output file exists in `docs/code-reviews/`. If missing, write the file manually from the subagent's output. **Detection signal:** code-reviewer agent returns "done" but `docs/code-reviews/` has no new file. **Fix:** add a post-invocation check: `ls docs/code-reviews/` and verify recency.

- **Cross-check board status against GitHub issues at sprint boundary.** During sprint boundary board compliance audit, compare `gh issue list --state closed` against board items still in non-Done statuses. Closed issues that remain at "In Progress" or "In Review" on the board are stale state — fix them before proceeding. This was a recurring finding across 5+ projects where issues were auto-closed by commit messages but board status was never updated.

- **Sprint plan must not contradict accepted ADRs.** If a sprint plan specifies product behavior that differs from an accepted ADR (e.g., plan says "on by default" but ADR says "off by default"), the ADR must be formally amended first. A sprint plan note is insufficient to override an ADR. **Detection signal:** sprint plan contradicts an ADR and no amendment PR exists. **Fix:** amend the ADR through the normal gate (Archie + Wei debate) before proceeding with the contradictory plan.

- **All sprint items must be on the board at planning time.** Pat must add every sprint item — committed and stretch — to the project board with "Ready" status during sprint planning. Items not on the board at the start of the sprint create friction when Grace tries to track status transitions, and they often skip "In Progress" and "In Review" entirely. **Detection signal:** sprint execution starts but `gh project item-list` shows fewer items than the sprint plan. **Fix:** Pat adds all items during planning; Grace verifies board count matches plan count before execution begins.

- **Spike work gets an abbreviated Done Gate.** For spike/research work (disposable code, no production users), apply a shortened gate: tests pass, results documented, relevant ADR updated, board moved to Done. The full 15-item checklist applies only to production code. **However:** if spike code is later reused (even partially) in production, the full gate must run on the reused portions. **Detection signal:** production code imports or copies from a spike directory. **Fix:** run full Done Gate on the reused code before merging.

- **Architecture docs describe contracts, not aspirations.** If an architecture doc says "the theme schema has a `pptx:` section," that must be true in code. Treat architecture claims as testable assertions. When you implement and discover you can't honor a stated constraint, update the doc to reflect reality — mark the section as "deferred" or "not yet implemented," don't leave it describing a future that doesn't exist. **Detection signal:** architecture doc describes capability that isn't in the codebase. **Fix:** doc reflects what IS, with clear markers for what's PLANNED.

## Volatile Knowledge

Some gotcha entries describe behavior of *external tools* (CLIs, SDKs, cloud APIs) rather than our own code. These entries are marked with ⚠️ *Volatile* and include a "verified" date and version.

**Convention:**
- Entries marked `⚠️ Volatile` are known to be time-sensitive. They were correct when verified but may have changed since.
- Before adopting a volatile pattern in a new project, re-verify it against the current tool version.
- After verification, update the "verified" date in the gotcha entry and the corresponding research doc.
- If a volatile pattern has changed, update both the gotcha and the research doc, then check downstream projects listed in the research doc for drift.

**Why not just delete stale entries?** Because "this used to be true and may have changed" is more useful than silence. A developer who hits a CLI hang and finds a volatile gotcha saying "stdin used to cause this" has a strong lead. A developer who finds nothing has to debug from scratch.

**Current volatile entries:**
- Claude CLI invocation patterns → `docs/research/claude-cli-invocation-patterns.md`
