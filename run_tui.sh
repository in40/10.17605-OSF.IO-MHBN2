#!/usr/bin/env bash
# Launch the smoke-test TUI with the LLM bearer token set.
# Key resolution order: $SC_KEY env -> $SMOKE_KEY_FILE (default ./.smoke_key) -> prompt.
# The key is NEVER hardcoded in this script.
set -euo pipefail
cd "$(dirname "$0")"

KEY_FILE="${SMOKE_KEY_FILE:-.smoke_key}"

if [ -z "${SC_KEY:-}" ]; then
  if [ -f "$KEY_FILE" ]; then
    SC_KEY="$(cat "$KEY_FILE")"
  else
    read -rsp "Enter LLM API key (bearer token): " SC_KEY
    echo
  fi
fi

if [ -z "${SC_KEY:-}" ]; then
  echo "ERROR: no API key provided." >&2
  exit 1
fi
export SC_KEY

VENV_PY=".venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
  echo "ERROR: $VENV_PY not found. Create the venv first:" >&2
  echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

exec "$VENV_PY" -m smoke_tui
