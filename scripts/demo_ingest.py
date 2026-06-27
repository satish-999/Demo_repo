#!/usr/bin/env python3
"""Load the bundled sample SRT/script into CineWeave for a quick smoke test."""

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "http://localhost:8000/api/v1/titles/ingest"


def main() -> int:
    payload = {
        "studio_name": "Demo Studio",
        "title_name": "Sample Dub POC",
        "language": "hi",
        "source_language": "te",
        "srt_path": str(ROOT / "fixtures" / "sample_hi.srt"),
        "script_path": str(ROOT / "fixtures" / "sample_te_script.txt"),
        "video_path": sys.argv[1] if len(sys.argv) > 1 else None,
        "audio_path": sys.argv[2] if len(sys.argv) > 2 else None,
    }
    req = urllib.request.Request(
        API,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as res:
        title = json.load(res)
    print(f"Ingested title: {title['id']}")
    print(f"Segments: {title['segment_count']} | Flagged: {title['flagged']} | Accepted: {title['accepted']}")
    print(f"Open UI: http://localhost:3000/titles/{title['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
