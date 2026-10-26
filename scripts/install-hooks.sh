#!/usr/bin/env bash
# Point git at the versioned hooks (scripts/hooks). Run once per clone; the setting is
# shared by all worktrees of the clone.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
chmod +x scripts/hooks/pre-push
git config core.hooksPath scripts/hooks
echo "core.hooksPath = $(git config core.hooksPath)"
