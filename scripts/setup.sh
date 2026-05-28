#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python -m venv .venv

# shellcheck source=/dev/null
source .venv/Scripts/activate
pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
fi
