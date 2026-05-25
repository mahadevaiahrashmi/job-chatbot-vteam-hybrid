---
agent-notes: { ctx: "volatile patterns for spawning claude CLI as subprocess", deps: [docs/process/gotchas.md], state: active, last: "coordinator@2026-03-30" }
---

# Claude CLI Invocation Patterns

> **Source:** predictasaurv2 `ClaudeCodeAdapter`, daily-news `claude-cli.ts` (commit `b296f4f`)
> **Reviewed:** 2026-03-30
> **CLI Version:** 2.1.87 (Claude Code)
> **Status:** Research — volatile knowledge, verify before adopting

## Why This Doc Exists

Two projects in this org independently learned the same 8 lessons about spawning `claude` as a subprocess. The second project (daily-news) had to rewrite its entire CLI backend to match patterns the first project (predictasaurv2) had already discovered. This doc captures those patterns so future projects start informed — but every pattern here describes *current CLI behavior* that may change. Treat this as a starting point for verification, not a specification.

## Staleness Policy

**Before adopting any pattern below:**

1. Check the "Reviewed" date above. If it's more than 3 months old, re-verify everything.
2. Run `claude --help` and `claude --version` to check for flag changes.
3. Web-search for Claude Code CLI changelog or release notes.
4. After verification, update the "Reviewed" date and "CLI Version" above.

If a pattern has changed, update it here and propagate the fix to downstream projects.

---

## Pattern 1: Prompt via `-p` Flag, Not stdin

**Problem:** Piping the prompt through stdin (`proc.stdin.write(...)`) causes hangs and reliability issues. The CLI expects interactive stdin or nothing.

**Fix:** Pass the prompt as a `-p` argument and set stdin to `'ignore'`.

```typescript
// WRONG — hangs or drops connections
const proc = spawn('claude', ['--print'], { stdio: 'pipe' });
proc.stdin.write(prompt);
proc.stdin.end();

// RIGHT — reliable, non-interactive
const proc = spawn('claude', ['--print', '-p', prompt], {
  stdio: ['ignore', 'pipe', 'pipe'],
});
```

**Why it works:** `-p` passes the prompt as a CLI argument. `stdin: 'ignore'` tells the subprocess there's no interactive input, so it doesn't wait for EOF.

**Related gotcha:** "execa v9 `stdin: 'pipe'` default hangs subprocesses" in `docs/process/gotchas.md`.

---

## Pattern 2: No `--bare` or `--output-format json`

**Problem:** These flags are either unsupported or incompatible with `--print` mode. Using them causes parsing failures or unexpected output formats.

**Fix:** Use `--print` only. The CLI returns plain text — parse JSON from that.

```typescript
// WRONG — flags cause issues
const args = ['--print', '--output-format', 'json', '--bare', '-p', prompt];

// RIGHT — plain text output, parse it yourself
const args = ['--print', '-p', prompt];
```

**Why:** `--print` is the non-interactive output mode. The CLI doesn't guarantee structured JSON output — it returns whatever the model says. If you need JSON, ask the model for JSON in the prompt and extract it from the text response.

---

## Pattern 3: Extract JSON from Plain Text Responses

**Problem:** Even when you prompt "respond with valid JSON only," models frequently wrap responses in markdown fences (` ```json ... ``` `). Direct `JSON.parse()` on the raw output fails.

**Fix:** Use a robust extraction function that handles fenced, unfenced, and embedded JSON.

```typescript
function extractJson(content: string): string {
  const trimmed = content.trim();

  // Try ```json ... ``` markdown fences
  const fenceMatch = trimmed.match(/```(?:json)?\s*\n?([\s\S]*?)\n?\s*```/);
  if (fenceMatch) return fenceMatch[1].trim();

  // Try raw JSON (starts with { or [)
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) return trimmed;

  // Find first { ... } block embedded in text
  const objMatch = trimmed.match(/(\{[\s\S]*\})/);
  if (objMatch) return objMatch[1];

  return trimmed;
}
```

**Note:** For Zod-validated structured output, the Anthropic *API* (not CLI) supports native tool-use-based structured output, which is more reliable. The CLI prompt-and-parse approach is a fallback for when you're using the CLI to avoid API costs.

---

## Pattern 4: Always Pass `--model` Explicitly

**Problem:** Relying on the CLI's default model makes behavior non-deterministic across environments and CLI versions.

**Fix:** Always specify the model.

```typescript
const args = ['--model', model, '--print', '-p', prompt];
```

**Why:** Default models change between CLI versions. Explicit model selection ensures reproducible behavior and makes tests meaningful.

---

## Pattern 5: Delete `CLAUDECODE` and `ANTHROPIC_API_KEY` Env Vars

**Problem:** The Claude CLI sets `CLAUDECODE=1` in its environment. If your app is itself running inside Claude Code (e.g., during development/testing), spawned `claude` subprocesses see this variable and refuse to run (anti-recursion guard). Separately, if `ANTHROPIC_API_KEY` is set, the CLI uses API credits instead of the user's subscription.

**Fix:** Strip both variables before spawning.

```typescript
const env = { ...process.env };
delete env.CLAUDECODE;        // Prevent nested CLI rejection
delete env.ANTHROPIC_API_KEY; // Use subscription auth, not API credits

const proc = spawn('claude', args, {
  stdio: ['ignore', 'pipe', 'pipe'],
  env,
});
```

```python
import os, subprocess

env = {k: v for k, v in os.environ.items()
       if k not in ('CLAUDECODE', 'ANTHROPIC_API_KEY')}

proc = subprocess.run(['claude', '--print', '-p', prompt], env=env, ...)
```

---

## Pattern 6: Validate Inputs Before Passing as Arguments

**Problem:** User-supplied content passed via `-p` could contain null bytes or control characters that break CLI argument parsing or enable injection.

**Fix:** Validate before spawning.

```typescript
function validateInput(value: string, label: string): void {
  if (value.includes('\0')) {
    throw new Error(`${label} contains null bytes — rejected for safety`);
  }
  if (/[\x00-\x08\x0B\x0C\x0E-\x1F]/.test(value)) {
    throw new Error(`${label} contains control characters — rejected for safety`);
  }
}

// Before spawning
validateInput(systemPrompt, 'system prompt');
validateInput(userPrompt, 'user prompt');
```

**Scope:** This is defense-in-depth for the spawn boundary. It doesn't replace application-level input validation.

---

## Pattern 7: Sanitize stderr for Sensitive Content

**Problem:** CLI error output may contain API keys, auth tokens, or other secrets — especially during auth failures or SDK errors.

**Fix:** Filter stderr before including it in error messages or logs.

```typescript
function sanitizeStderr(stderr: string): string {
  const MAX_LEN = 500;
  const truncated = stderr.slice(0, MAX_LEN);
  const lines = truncated.split('\n');
  const safe = lines.filter(
    (line) => !/\b(key|token|secret|password|credential|auth)\b/i.test(line),
  );
  const result = safe.join('\n');
  return stderr.length > MAX_LEN ? `${result} [truncated]` : result;
}
```

**Also sanitize error messages from the Anthropic SDK:**

```typescript
function sanitizeError(message: string): string {
  return message
    .replace(/\bsk-ant-[\w-]{10,}\b/g, '[REDACTED]')
    .replace(/\bsk-[\w-]{10,}\b/g, '[REDACTED]');
}
```

---

## Pattern 8: Settle Guard for Timeout Handling

**Problem:** When spawning a subprocess with a timeout, multiple event handlers (`error`, `close`, timeout callback) can race and resolve/reject the promise more than once.

**Fix:** Use a settle guard — a closure that ensures only the first resolution wins.

```typescript
function spawnWithTimeout(args: string[], timeout: number): Promise<string> {
  return new Promise((resolve, reject) => {
    let settled = false;
    let timedOut = false;

    const settle = (fn: () => void) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      fn();
    };

    const proc = spawn('claude', args, {
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    const timer = setTimeout(() => {
      timedOut = true;
      proc.kill('SIGTERM');
      settle(() => reject(new Error(`CLI timeout after ${timeout}ms`)));
    }, timeout);

    const chunks: Buffer[] = [];
    proc.stdout.on('data', (chunk) => chunks.push(chunk));

    proc.on('error', (err) => {
      settle(() => reject(err));
    });

    proc.on('close', (code) => {
      if (timedOut) return; // already settled by timeout
      const content = Buffer.concat(chunks).toString('utf-8');
      settle(() => {
        if (code !== 0) reject(new Error(`CLI exited with code ${code}`));
        else resolve(content);
      });
    });
  });
}
```

**Why not `AbortController`?** It works for `fetch` and some Node APIs, but `child_process.spawn` doesn't natively support it. The settle guard is more explicit and handles all three race conditions (error, close, timeout) uniformly.

---

## Token Usage Estimation

The CLI does not report token usage or cost. If you need usage estimates for logging/budgeting:

```typescript
// Rough estimate: ~4 characters per token
const inputTokens = Math.ceil((systemPrompt.length + userPrompt.length) / 4);
const outputTokens = Math.ceil(response.length / 4);
```

This is a rough heuristic. For accurate usage data, use the Anthropic API directly.

---

## CLI vs API: When to Use Which

| Concern | Claude CLI (`--print`) | Anthropic API (SDK) |
|---------|----------------------|-------------------|
| **Auth** | User's subscription | API key (per-token billing) |
| **Structured output** | Prompt-and-parse + retry | Native tool-use (reliable) |
| **Token usage** | Estimated | Exact |
| **Latency** | Process spawn overhead | Direct HTTP |
| **Best for** | Cost-sensitive batch work | Production pipelines |

Both predictasaurv2 and daily-news use a **dual adapter** pattern: CLI for cost-sensitive work, API for reliability-sensitive work, behind a common interface.

---

## Downstream Projects Using These Patterns

| Project | File | Notes |
|---------|------|-------|
| predictasaurv2 | `packages/llm/src/claude-code-adapter.ts` | Origin of all 8 patterns |
| daily-news | `src/backends/claude-cli.ts` | Adopted via refactor `b296f4f` |

When updating patterns here, check these files for drift.
