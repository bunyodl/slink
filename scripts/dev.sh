#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .venv/Scripts/activate ]]; then
  echo "Run ./scripts/setup.sh first" >&2
  exit 1
fi

# shellcheck source=/dev/null
source .venv/Scripts/activate
uvicorn app.main:app --reload
