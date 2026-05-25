---
agent-notes: { ctx: "tracking adapter switchboard and registry", deps: [CLAUDE.md, docs/integrations/github-projects.md, docs/integrations/jira.md], state: active, last: "sato@2026-02-21" }
---

# Tracking Integrations

This directory contains adapter files that define how the vteam-hybrid methodology interacts with external tracking systems. Each adapter maps the methodology's board operations (status transitions, issue CRUD, sprint labeling) to a specific tool's CLI or API.

## Active Adapter

The active adapter is declared in `CLAUDE.md` via an HTML comment:

```html
<!-- tracking-adapter: github-projects -->
```

Agents read this comment to determine which adapter file to consult for board commands. If the comment is missing or empty, **github-projects** is the default.

## Switching Adapters

1. Change the `<!-- tracking-adapter: -->` comment in `CLAUDE.md` to the new adapter name.
2. Read the corresponding adapter file in this directory for setup prerequisites.
3. Run the adapter's pre-flight check to verify access.

## Available Adapters

| Adapter | File | Status |
|---------|------|--------|
| GitHub Projects v2 | `github-projects.md` | Canonical -- production-tested |
| Jira | `jira.md` | Draft -- untested, needs validation |

## Required Status Model

All adapters must support **5 ordered statuses**:

**Backlog** --> **Ready** --> **In Progress** --> **In Review** --> **Done**

This is a methodology requirement, not a tool requirement. If the target tool does not natively support all 5, the adapter must document how to add the missing ones.
