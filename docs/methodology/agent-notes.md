---
agent-notes: { ctx: "agent-notes format spec for all file types", deps: [CLAUDE.md], state: canonical, last: "archie@2026-02-12" }
---

# Agent-Notes Protocol

Agent-notes are compressed, structured metadata at the top of every file (except pure JSON) that bootstrap Claude's context without requiring a full file read. They are **not meant for human consumption** — they are dense key-value annotations optimized for agent context loading.

## Why

Claude Code sessions start cold. Reading every file to understand a codebase is expensive and slow. Agent-notes provide a ~50-word summary that lets an agent decide whether to read the full file, understand its role in the system, and know who last touched it — all before reading line 1.

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `ctx` | string | Purpose of this file in <10 words |
| `deps` | string[] | Files this file directly depends on or references |
| `state` | enum | `draft` / `active` / `canonical` / `deprecated` / `stub` |
| `last` | string | `<agent-name>@<YYYY-MM-DD>` — who last modified and when |

## Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `key` | string[] | Critical facts an agent must know (max 3 items) |
| `hot` | string[] | Performance or safety warnings |
| `invariants` | string[] | Formal invariants this file must maintain |
| `stale-risk` | string | What makes this file likely to go stale (e.g., "external API changes") |

## Format by File Type

### Markdown (.md)

YAML frontmatter with an `agent-notes` key:

```yaml
---
agent-notes: { ctx: "ADR for TDD workflow", deps: [CLAUDE.md, docs/methodology/personas.md], state: active, last: "archie@2026-02-12" }
---

# Document title here
```

If the file already has YAML frontmatter, add `agent-notes` as an additional key.

### TypeScript / JavaScript (.ts, .js, .tsx, .jsx)

Single-line comment at the top of the file (after any shebang):

```typescript
// agent-notes: { ctx: "React hook for auth state", deps: ["src/api/auth.ts", "src/types.ts"], state: active, last: "sato@2026-02-12" }
```

### Python (.py)

Single-line comment after any shebang and encoding declarations:

```python
# agent-notes: { ctx: "CLI entry point for daily picker", deps: ["config.py", "strategies/"], state: active, last: "sato@2026-02-12" }
```

### Rust (.rs)

Single-line comment at the top:

```rust
// agent-notes: { ctx: "phase vocoder core FFT pipeline", deps: ["crate::fft", "crate::window"], state: active, last: "sato@2026-02-12", hot: ["perf-critical inner loop"] }
```

### Svelte (.svelte)

HTML comment at the top (before `<script>`):

```svelte
<!-- agent-notes: { ctx: "waveform display component", deps: ["src/lib/stores/audio.ts"], state: active, last: "dani@2026-02-12" } -->
```

### CSS / SCSS (.css, .scss)

Comment at the top:

```css
/* agent-notes: { ctx: "design tokens and theme variables", deps: [], state: canonical, last: "dani@2026-02-12" } */
```

### YAML (.yaml, .yml)

Comment at the top (before any `---` document separator):

```yaml
# agent-notes: { ctx: "CI pipeline definition", deps: [Dockerfile, package.json], state: active, last: "ines@2026-02-12" }
```

### TOML (.toml)

Comment at the top:

```toml
# agent-notes: { ctx: "Rust workspace config", deps: ["crates/*/Cargo.toml"], state: canonical, last: "sato@2026-02-12" }
```

### Shell (.sh, .bash, .zsh)

Comment after the shebang:

```bash
#!/usr/bin/env bash
# agent-notes: { ctx: "launch parallel agent teams in tmux", deps: [".claude/agents/"], state: active, last: "ines@2026-02-12" }
```

### Dockerfile

Comment at the top:

```dockerfile
# agent-notes: { ctx: "dev container with Rust + Node + audio libs", deps: [".devcontainer/devcontainer.json"], state: active, last: "ines@2026-02-12" }
```

### Agent definition files (.claude/agents/*.md)

HTML comment after the YAML frontmatter closing `---`:

```markdown
---
name: sato
description: Principal software engineer
tools: Read, Write, Edit, Bash, Grep, Glob
model: inherit
maxTurns: 25
---
<!-- agent-notes: { ctx: "principal SDE, TDD green phase", deps: [docs/methodology/personas.md, docs/methodology/phases.md], state: canonical, last: "archie@2026-02-12" } -->
```

### Command files (.claude/commands/*.md)

HTML comment at the top of the file (before the first line of content):

```markdown
<!-- agent-notes: { ctx: "kickoff discovery workflow", deps: [docs/methodology/personas.md], state: active, last: "cam@2026-02-12" } -->
Run a full discovery workflow for: $ARGUMENTS
```

## Excluded File Types

- **Pure JSON** (.json): Cannot contain comments. The filename and schema are self-documenting.
- **Lock files** (package-lock.json, Cargo.lock, etc.): Auto-generated, never manually annotated.
- **Binary files**: Not applicable.
- **.gitkeep files**: Empty placeholder files, no annotation needed.

## Rules

1. **Every new file gets agent-notes.** No exceptions for non-excluded types.
2. **Every edit updates `last`.** When you modify a file, update the `last` field to your agent name and today's date.
3. **Keep `ctx` under 10 words.** If you can't describe the file's purpose in 10 words, you don't understand it well enough.
4. **`deps` lists direct dependencies only.** Not transitive. If A depends on B and B depends on C, A's deps list B but not C.
5. **`state` must be accurate.** Don't leave a file as `draft` once it's being used. Don't leave it as `active` once it's superseded.
6. **Don't bloat optional fields.** Only add `hot`, `invariants`, or `key` when they contain genuinely critical information. Most files only need the required fields.
7. **Agent-notes are for agents.** Don't add human-readable explanations. Keep it dense.
