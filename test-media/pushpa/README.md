# Place your test movie files here

## Pushpa 2 — Apology scene (example)

Copy your files into this folder with simple names:

```
test-media/pushpa/
  pushpa_apology.mp4    ← video clip (~3 min)
  pushpa_apology.srt    ← Hindi dub subtitles (required)
  pushpa_apology.mp3    ← audio only (optional if mp4 has audio)
  pushpa_script_te.txt  ← Telugu script (optional, improves semantic scoring)
```

## Ingest via web UI

1. Run `./scripts/start-all.sh` from project root
2. Open http://localhost:3000/ingest
3. Upload the files above

## Ingest via API (local paths)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/titles/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "title_name": "Pushpa 2 Apology Scene",
    "language": "hi",
    "source_language": "te",
    "video_path": "ABSOLUTE_PATH/test-media/pushpa/pushpa_apology.mp4",
    "srt_path": "ABSOLUTE_PATH/test-media/pushpa/pushpa_apology.srt"
  }'
```

Replace `ABSOLUTE_PATH` with your project root (e.g. `/home/you/cineweave-rae`).
