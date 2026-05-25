---
agent-notes: { ctx: "Jira board adapter -- untested draft", deps: [CLAUDE.md, docs/integrations/README.md], state: draft, last: "sato@2026-02-21", key: ["untested -- needs validation on real Jira instance", "covers Jira Cloud REST API v3 and jira CLI", "sprint model uses Jira native sprints not labels"] }
---

# Jira Adapter

> **STATUS: DRAFT -- UNTESTED.** This adapter has not been validated against a live Jira instance. Commands and API paths are based on Jira Cloud REST API v3 documentation. Expect adjustments when first used in production.

Maps vteam-hybrid board operations to Jira Cloud. Covers both the `jira` CLI (Atlassian's official Go CLI) and raw `curl` commands against the REST API.

## Prerequisites

**Option A: Jira CLI (preferred)**
- Install: `go install github.com/ankitpokhrel/jira-cli/cmd/jira@latest` (community CLI, widely used)
- Or use Atlassian's official CLI if available.
- Authenticate: `jira init` (interactive setup with Jira URL, email, API token).

**Option B: curl + API Token**
- Generate an API token at https://id.atlassian.com/manage-profile/security/api-tokens
- Set environment variables:
  ```bash
  export JIRA_BASE_URL="https://your-domain.atlassian.net"
  export JIRA_EMAIL="your-email@example.com"
  export JIRA_API_TOKEN="your-api-token"
  ```

## Setup (CLAUDE.md Config)

The following HTML comments in `CLAUDE.md` configure Jira operations:

```html
<!-- tracking-adapter: jira -->
<!-- jira-project-key: -->
<!-- jira-base-url: -->
```

- `jira-project-key`: The Jira project key (e.g., `PROJ`, `VT`). Found in the project URL or settings.
- `jira-base-url`: The Jira Cloud instance URL (e.g., `https://your-domain.atlassian.net`).

## Pre-Flight Check

Run before any session that touches the board.

```bash
# Option A: Jira CLI
jira me  # Verify authentication -- should print current user info

# Option B: curl
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/3/myself" | jq '.displayName'
```

Verify the project exists and is accessible:

```bash
# Option A: Jira CLI
jira project list | grep <PROJECT_KEY>

# Option B: curl
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/3/project/<PROJECT_KEY>" | jq '.name'
```

If any check fails, **STOP**. Report the failure and ask the user to fix authentication or project access.

## Board and Project Setup

Unlike GitHub Projects, Jira boards typically pre-exist. The setup task is ensuring the workflow has the correct statuses.

### Verify Required Statuses

The methodology requires 5 statuses: **Backlog, Ready, In Progress, In Review, Done**.

```bash
# List available statuses for the project
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/3/project/<PROJECT_KEY>/statuses" | \
  jq '.[].statuses[].name' | sort -u
```

Common mappings from default Jira workflows:

| Methodology Status | Jira Default | Notes |
|-------------------|-------------|-------|
| Backlog | Backlog | Usually exists |
| Ready | Selected for Development / Ready | May need to add |
| In Progress | In Progress | Usually exists |
| In Review | In Review / Code Review | May need to add |
| Done | Done | Usually exists |

**If statuses are missing**, they must be added via Jira's workflow editor (Project Settings -> Workflows -> Edit). This typically requires Jira admin access and cannot be done via API alone. Document the required workflow changes and ask the user or Jira admin to configure them.

### Record Status IDs

Jira transitions use numeric IDs, not status names. Look up the transition IDs for your project:

```bash
# Get transitions for an existing issue (need at least one issue)
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/3/issue/<PROJECT_KEY>-1/transitions" | \
  jq '.transitions[] | {id, name}'
```

Record these IDs in a session cache or in `CLAUDE.md` comments for reuse:

```html
<!-- jira-transition-in-progress: 21 -->
<!-- jira-transition-in-review: 31 -->
<!-- jira-transition-done: 41 -->
```

Note: Transition IDs vary per project and workflow. The numbers above are examples.

## Status Transitions

Move an issue to a new status by executing a transition.

```bash
# Option A: Jira CLI
jira issue move <PROJECT_KEY>-<NUMBER> "In Progress"
jira issue move <PROJECT_KEY>-<NUMBER> "In Review"
jira issue move <PROJECT_KEY>-<NUMBER> "Done"

# Option B: curl (using transition ID)
curl -s -X POST \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transition": {"id": "<TRANSITION_ID>"}}' \
  "$JIRA_BASE_URL/rest/api/3/issue/<PROJECT_KEY>-<NUMBER>/transitions"
```

**Rules** (same as all adapters):
- Per-item transitions only. Never batch-update.
- Ordered transitions: In Progress -> In Review -> Done. No skipping.
- Move to In Progress BEFORE starting work.
- Move to In Review AFTER implementation, BEFORE code review.

## Issue Operations

### Create an Issue

```bash
# Option A: Jira CLI
jira issue create \
  --project <PROJECT_KEY> \
  --type Task \
  --summary "feat: implement user authentication" \
  --body "Acceptance criteria:
- Users can sign in with email/password
- Session persists across browser refresh" \
  --label "sprint:1"

# Option B: curl
curl -s -X POST \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "project": {"key": "<PROJECT_KEY>"},
      "issuetype": {"name": "Task"},
      "summary": "feat: implement user authentication",
      "description": {
        "type": "doc",
        "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Acceptance criteria:\n- Users can sign in with email/password\n- Session persists across browser refresh"}]}]
      },
      "labels": ["sprint:1"]
    }
  }' \
  "$JIRA_BASE_URL/rest/api/3/issue"
```

### List Issues

```bash
# Option A: Jira CLI
jira issue list --project <PROJECT_KEY> --status "~Done"  # Exclude done
jira issue list --project <PROJECT_KEY> --label "sprint:1"

# Option B: curl (JQL query)
curl -s -G \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  --data-urlencode "jql=project = <PROJECT_KEY> AND status != Done ORDER BY created DESC" \
  "$JIRA_BASE_URL/rest/api/3/search" | jq '.issues[] | {key, summary: .fields.summary, status: .fields.status.name}'
```

### Close an Issue

```bash
# Transition to Done (use the Done transition ID)
jira issue move <PROJECT_KEY>-<NUMBER> "Done"

# Or add a resolution
curl -s -X POST \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transition": {"id": "<DONE_TRANSITION_ID>"}, "fields": {"resolution": {"name": "Done"}}}' \
  "$JIRA_BASE_URL/rest/api/3/issue/<PROJECT_KEY>-<NUMBER>/transitions"
```

### Add a Label

```bash
# Option A: Jira CLI
jira issue edit <PROJECT_KEY>-<NUMBER> --label "sprint:2"

# Option B: curl
curl -s -X PUT \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"update": {"labels": [{"add": "sprint:2"}]}}' \
  "$JIRA_BASE_URL/rest/api/3/issue/<PROJECT_KEY>-<NUMBER>"
```

## Sprint Management

Jira has native sprint support via its Agile/Scrum boards. The methodology can use either approach:

### Option 1: Jira Native Sprints (Recommended for Jira)

```bash
# List boards
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/agile/1.0/board?projectKeyOrId=<PROJECT_KEY>" | jq '.values[] | {id, name}'

# List sprints for a board
curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/agile/1.0/board/<BOARD_ID>/sprint" | jq '.values[] | {id, name, state}'

# Create a sprint
curl -s -X POST \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Sprint 1", "originBoardId": <BOARD_ID>}' \
  "$JIRA_BASE_URL/rest/agile/1.0/sprint"

# Move issues into a sprint
curl -s -X POST \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"issues": ["<PROJECT_KEY>-1", "<PROJECT_KEY>-2"]}' \
  "$JIRA_BASE_URL/rest/agile/1.0/sprint/<SPRINT_ID>/issue"

# Start a sprint
curl -s -X POST \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"state": "active", "startDate": "2026-02-21T00:00:00.000Z", "endDate": "2026-03-07T00:00:00.000Z"}' \
  "$JIRA_BASE_URL/rest/agile/1.0/sprint/<SPRINT_ID>"

# Complete a sprint (moves incomplete issues to backlog or next sprint)
curl -s -X POST \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"state": "closed"}' \
  "$JIRA_BASE_URL/rest/agile/1.0/sprint/<SPRINT_ID>"
```

### Option 2: Labels (Fallback)

If native sprints are not available (e.g., Kanban board without sprint support), fall back to the same label-based approach used by the GitHub Projects adapter:

```bash
# Use labels like "sprint:1", "sprint:2"
# See Issue Operations > Add a Label above
```

## Differences from GitHub Projects Adapter

| Aspect | GitHub Projects | Jira |
|--------|----------------|------|
| Status changes | Field edit on project item | Workflow transition on issue |
| Status IDs | Option IDs from field-list | Transition IDs from issue |
| Sprint tracking | Labels (`sprint:N`) | Native sprints (preferred) or labels |
| Board creation | `gh project create` | Usually pre-exists; admin setup |
| Adding statuses | GraphQL mutation | Workflow editor (admin) |
| Issue-board link | `gh project item-add` | Automatic (board shows project issues) |

## Known Limitations and Open Questions

> These must be resolved when this adapter is first used on a real Jira instance.

1. **Workflow variation**: Jira workflows are highly customizable. Transition IDs and available statuses differ per project. The recipes above assume a standard Scrum workflow.
2. **Admin access**: Adding statuses to a Jira workflow requires admin permissions. The adapter cannot self-configure like the GitHub Projects adapter can.
3. **Description format**: Jira Cloud v3 uses Atlassian Document Format (ADF) for issue descriptions, not plain text or Markdown. The curl examples above use minimal ADF; complex descriptions may need richer structures.
4. **Rate limiting**: Jira Cloud has rate limits. Bulk operations (creating many issues at sprint start) may need throttling.
5. **jira CLI compatibility**: The community `jira-cli` tool (ankitpokhrel/jira-cli) is used in examples. Its command syntax may differ from other Jira CLI tools.
6. **Two-way sync**: This adapter is one-directional (agents push to Jira). It does not handle Jira webhook events or external status changes made by humans in the Jira UI.
