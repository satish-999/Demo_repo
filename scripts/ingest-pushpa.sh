#!/usr/bin/env bash
# Ingest Pushpa test files from test-media/pushpa/ (if present)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API="${BACKEND_URL:-http://127.0.0.1:8000}/api/v1/titles/ingest"
DIR="$ROOT/test-media/pushpa"

pick() {
  local pattern="$1"
  find "$DIR" -maxdepth 1 -iname "$pattern" 2>/dev/null | head -1
}

SRT="$(pick '*.srt')"
VIDEO="$(pick '*.mp4')"
AUDIO="$(pick '*.mp3')"

if [ -z "$SRT" ]; then
  echo "No .srt found in $DIR"
  echo "Place pushpa_apology.srt in test-media/pushpa/ or use the web UI."
  exit 1
fi

python3 - "$API" "$SRT" "$VIDEO" "$AUDIO" <<'PY'
import json, sys, urllib.request
api, srt, video, audio = sys.argv[1:5]
payload = {
    "studio_name": "Demo Studio",
    "title_name": "Pushpa 2 Apology Scene",
    "language": "hi",
    "source_language": "te",
    "srt_path": srt,
}
if video:
    payload["video_path"] = video
if audio:
    payload["audio_path"] = audio
req = urllib.request.Request(
    api,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req) as res:
    title = json.load(res)
print(f"Title ID: {title['id']}")
print(f"Segments: {title['segment_count']} | Flagged: {title['flagged']} | Accepted: {title['accepted']}")
print(f"Open: http://localhost:3000/titles/{title['id']}")
PY
