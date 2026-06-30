#!/usr/bin/env bash
# Start both CineWeave servers. Run from project root: ./scripts/start-all.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:$PATH"

echo "Starting backend on :8000 and frontend on :3000"
echo "Press Ctrl+C to stop both."

trap 'kill 0' EXIT

(
  cd "$ROOT/backend"
  PYTHONPATH="$ROOT/backend" python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) &

(
  cd "$ROOT/frontend"
  npm run dev -- --hostname 0.0.0.0 --port 3000
) &

wait
