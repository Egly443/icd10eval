#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KEY_FILE="$PROJECT_DIR/.env.local"

if ! git -C "$PROJECT_DIR" check-ignore -q .env.local; then
  echo "Refusing to save a secret: .env.local is not ignored by Git." >&2
  exit 1
fi

printf "Paste your NEW OpenAI API key, then press Enter (input is hidden): " >&2
IFS= read -r -s BENCHMARK_API_KEY
printf "\n" >&2

if [[ "$BENCHMARK_API_KEY" != sk-* || ${#BENCHMARK_API_KEY} -lt 40 ]]; then
  unset BENCHMARK_API_KEY
  echo "That does not look like an OpenAI API key; nothing was saved." >&2
  exit 1
fi

umask 077
printf 'OPENAI_API_KEY=%q\n' "$BENCHMARK_API_KEY" > "$KEY_FILE"
unset BENCHMARK_API_KEY
chmod 600 "$KEY_FILE"

echo "Key saved to .env.local with owner-only permissions."
echo "Reply 'done' in Codex and the benchmark can be run without displaying the key."
