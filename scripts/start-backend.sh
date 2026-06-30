#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:$PATH"

echo "==> Starting CineWeave backend on http://localhost:8000"
cd "$ROOT/backend"
PYTHONPATH="$ROOT/backend" python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
