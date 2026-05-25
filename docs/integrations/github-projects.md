---
agent-notes: { ctx: "GitHub Projects v2 board adapter with gh CLI recipes", deps: [CLAUDE.md, .claude/agents/grace.md, .claude/commands/kickoff.md], state: canonical, last: "sato@2026-02-21", key: ["definitive gh CLI reference for board ops", "5 statuses required via GraphQL mutation", "per-item transitions only -- never batch"] }
---

# GitHub Projects v2 Adapter

Definitive reference for all GitHub Projects board operations. Agents should consult this file instead of duplicating `gh` recipes inline.

## Prerequisites

- **GitHub CLI** (`gh`) version 2.x+ installed and on PATH.
- **Auth scopes**: `project`, `repo`, `read:org` (if using org-owned projects). Run `gh auth status` to verify.
- **Project type**: GitHub Projects v2 (not classic Projects). Classic Projects use a different API and are not supported.

## Setup (CLAUDE.md Config)

The following HTML comments in `CLAUDE.md` configure board operations:

```html
<!-- tracking-adapter: github-projects -->
<!-- project-number: -->
<!-- project-owner: -->
```

- `project-number`: The numeric project ID visible in the GitHub Projects URL.
- `project-owner`: The GitHub user or org that owns the project. Use `@me` for the authenticated user.

These are populated during `/kickoff` Phase 5. All commands below use `<NUMBER>` and `<OWNER>` as placeholders for these values.

## Pre-Flight Check

Run before any session that touches the board. All three must pass.

```bash
# 1. Verify authentication
gh auth status

# 2. Verify project-number is configured (read from CLAUDE.md)
# If the comment is empty or missing, STOP and run kickoff Phase 5.

# 3. Verify board access and status field
gh project field-list <NUMBER> --owner <OWNER> --format json
# Confirm the "Status" field exists with all 5 options:
#   Backlog, Ready, In Progress, In Review, Done
```

If any check fails, **STOP**. Do not proceed with board operations. Report the failure and ask the user to fix it.

## Board Creation

Used during `/kickoff` Phase 5. Not needed after initial setup.

### Step 1: Create and Link

```bash
# Detect repo owner and name
gh repo view --json owner,name

# Create the project
gh project create --title "<project-name>" --owner @me

# Link the project to this repo
gh project link <NUMBER> --owner @me --repo <owner>/<repo>
```

### Step 2: Configure Status Field

GitHub Projects v2 creates only default statuses (Todo, In Progress, Done). The methodology requires 5. Use a GraphQL mutation to replace them.

```bash
# Get the project node ID and Status field ID
gh project list --owner <OWNER> --format json
# Note the project's node ID (id field)

gh project field-list <NUMBER> --owner <OWNER> --format json
# Note the Status field's ID

# Replace status options with the full set
gh api graphql -f query='
  mutation {
    updateProjectV2Field(input: {
      projectId: "<PROJECT_NODE_ID>"
      fieldId: "<STATUS_FIELD_ID>"
      name: "Status"
      singleSelectOptions: [
        {name: "Backlog", color: GRAY, description: "Not yet scheduled"}
        {name: "Ready", color: BLUE, description: "Scheduled for current sprint"}
        {name: "In Progress", color: YELLOW, description: "Actively being worked on"}
        {name: "In Review", color: ORANGE, description: "Implementation done, under review"}
        {name: "Done", color: GREEN, description: "Completed and verified"}
      ]
    }) {
      projectV2Field { ... on ProjectV2SingleSelectField { options { id name } } }
    }
  }'

# VERIFY all 5 statuses exist
gh project field-list <NUMBER> --owner <OWNER> --format json
```

**Do NOT proceed to issue creation until all 5 statuses are confirmed.** If the GraphQL mutation fails, try the GitHub web UI as a fallback.

### Step 3: Record Metadata in CLAUDE.md

After creation, update `CLAUDE.md` with:
- `project-number` and `project-owner` comments
- Status field ID
- Option IDs for each status (Backlog, Ready, In Progress, In Review, Done)

This metadata eliminates repeated field lookups in future sessions.

## ID Lookups

Most board operations require three IDs. Look these up once per session and cache them.

```bash
# Project node ID (needed for item-edit)
gh project list --owner <OWNER> --format json
# Find the project -> note its "id" field (the node ID)

# Status field ID and option IDs
gh project field-list <NUMBER> --owner <OWNER> --format json
# Find the "Status" field -> note its field ID
# Find each option (Backlog, Ready, In Progress, In Review, Done) -> note their option IDs

# Item IDs (maps issues to board items)
gh project item-list <NUMBER> --owner <OWNER> --format json
# Find the item matching your issue number -> note its item ID
```

## Status Transitions

Move an item to a new status. Requires: project node ID, item ID, status field ID, target status option ID.

```bash
gh project item-edit \
  --project-id <PROJECT_NODE_ID> \
  --id <ITEM_ID> \
  --field-id <STATUS_FIELD_ID> \
  --single-select-option-id <STATUS_OPTION_ID>
```

**Rules:**
- **Per-item transitions only.** Never batch-update all items. Each item transitions individually as work progresses.
- **Ordered transitions.** Items must pass through In Progress -> In Review -> Done. Jumping directly to Done is a process violation.
- **Move to In Progress BEFORE starting work**, not after.
- **Move to In Review AFTER implementation, BEFORE code review.**

## Issue Operations

### Create an Issue

```bash
# Sprint issue (labeled for current sprint)
gh issue create \
  --title "feat: implement user authentication" \
  --body "Acceptance criteria:
- Users can sign in with email/password
- Session persists across browser refresh" \
  --label "sprint:1"

# Backlog issue (no sprint label)
gh issue create \
  --title "chore: set up monitoring dashboard" \
  --body "Track API latency, error rates, and throughput."
```

### Add Issue to Project

```bash
gh project item-add <NUMBER> --owner <OWNER> --url <issue-url>
```

### List Issues

```bash
# All open issues
gh issue list

# Issues for a specific sprint
gh issue list --label "sprint:1"

# Issues with details
gh issue list --json number,title,state,labels
```

### Close an Issue

```bash
# Close with a reference (usually done via commit message "Closes #N")
gh issue close <NUMBER>
```

## Sprint Labeling

Sprints are tracked via labels, not a custom field.

```bash
# Create sprint labels (do this once)
gh label create "sprint:1" --description "Sprint 1" --color 0E8A16
gh label create "sprint:2" --description "Sprint 2" --color 0E8A16

# Add sprint label to an issue
gh issue edit <NUMBER> --add-label "sprint:2"

# Remove old sprint label (when rolling over)
gh issue edit <NUMBER> --remove-label "sprint:1"
```

## Board Health Verification

Run at sprint start and sprint boundary (Grace's responsibility).

1. **All 5 statuses exist:** `gh project field-list` confirms Backlog, Ready, In Progress, In Review, Done.
2. **No skipped statuses:** List all Done items and verify they passed through In Progress and In Review.
3. **No stale In Progress:** Items stuck in In Progress for the entire sprint indicate abandoned work or missed transitions.
