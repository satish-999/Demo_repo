#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:$PATH"

echo "==> CineWeave RAE backend — http://127.0.0.1:8000"
cd "$ROOT/backend"
PYTHONPATH="$ROOT/backend" python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
