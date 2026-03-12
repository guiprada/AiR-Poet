#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Install linting tools
pip install pyflakes --quiet

# Set PYTHONPATH so tests and modules resolve correctly from the project root
echo 'export PYTHONPATH="$CLAUDE_PROJECT_DIR"' >> "$CLAUDE_ENV_FILE"
