#!/usr/bin/env bash
# First-time setup for cineweave-rae
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:$PATH"

echo "==> CineWeave RAE setup"
echo "Project: $ROOT"

if [ ! -f "$ROOT/.env" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Created .env from .env.example"
fi

mkdir -p "$ROOT/test-media/pushpa" "$ROOT/test-media/uploads" "$ROOT/backend/data"

echo "==> Installing Python dependencies"
pip3 install -r "$ROOT/backend/requirements.txt"

echo "==> Installing Node dependencies"
(cd "$ROOT/frontend" && npm install)

echo ""
echo "Setup complete."
echo ""
echo "Next steps:"
echo "  1. Put your test files in:  test-media/pushpa/"
echo "  2. Start the app:           ./scripts/start-all.sh"
echo "  3. Open:                      http://localhost:3000/ingest"
echo ""
