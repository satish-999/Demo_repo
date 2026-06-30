#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Starting CineWeave frontend on http://localhost:3000"
cd "$ROOT/frontend"
export NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev -- --hostname 0.0.0.0 --port 3000
