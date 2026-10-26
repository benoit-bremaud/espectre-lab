#!/usr/bin/env bash
# Point git at the versioned hooks (scripts/hooks). Run once per clone; the setting is
# shared by all worktrees of the clone. Requires gitleaks on PATH (the hook fails closed).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath scripts/hooks
echo "core.hooksPath = $(git config core.hooksPath)"
