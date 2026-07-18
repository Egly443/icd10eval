#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/scripts/build_exemplars.py"
"$PROJECT_DIR/.venv/bin/pytest"
bash -n "$PROJECT_DIR/scripts/start.sh" "$PROJECT_DIR/scripts/check.sh"
echo "Release checks passed."
