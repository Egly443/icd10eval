#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  python3 -m venv "$VENV_DIR"
fi

if ! "$VENV_DIR/bin/python" -c "import fastapi, synthetic_episode_studio" >/dev/null 2>&1; then
  "$VENV_DIR/bin/pip" install -e "$PROJECT_DIR"
fi

exec "$VENV_DIR/bin/uvicorn" synthetic_episode_studio.main:app --app-dir "$PROJECT_DIR/src" --host 127.0.0.1 --port "${PORT:-8000}"
