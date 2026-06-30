#!/usr/bin/env bash
# Start CineWeave RAE — backend (:8000) + frontend (:3000)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:$PATH"

if [ -f "$ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ROOT/.env"
  set +a
fi

echo "=========================================="
echo "  CineWeave RAE"
echo "  Backend:  http://127.0.0.1:8000"
echo "  Frontend: http://localhost:3000"
echo "  Ingest:   http://localhost:3000/ingest"
echo "=========================================="
echo "Press Ctrl+C to stop both servers."
echo ""

trap 'kill 0' EXIT

(
  cd "$ROOT/backend"
  PYTHONPATH="$ROOT/backend" python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) &

(
  cd "$ROOT/frontend"
  export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://127.0.0.1:8000}"
  npm run dev -- --hostname 0.0.0.0 --port 3000
) &

wait
