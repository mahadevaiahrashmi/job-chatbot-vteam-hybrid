#!/usr/bin/env bash
# agent-notes: { ctx: "TeammateIdle hook preventing idle with uncommitted changes", deps: [], state: active, last: "sato@2026-03-28" }
#
# TeammateIdle hook — prevents teammates from going idle with uncommitted changes.
#
# Exit codes:
#   0 = no uncommitted changes, safe to idle
#   2 = uncommitted changes present — blocks idle

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
cd "$PROJECT_DIR"

# Check for modified tracked files (ignore untracked)
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  echo "[teammate-idle] You have uncommitted changes. Commit your work before going idle."
  echo ""
  git status --short
  exit 2
fi

exit 0
