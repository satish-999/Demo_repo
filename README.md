# CineWeave RAE — Proof of Concept

A **small, testable slice** of CineWeave you can run on a released movie clip (5–15 minutes recommended).

This POC implements the core heart of the product:

1. **Ingest** — video/audio + SRT (+ optional script)
2. **Segment compiler** — one subtitle cue = one review segment with stable IDs
3. **Hard gates** — rights, spec, consent (POC stubs)
4. **Soft scorers** — sync timing, semantic fidelity, performance energy
5. **Verdict** — ACCEPTED / FLAGGED / REJECTED per segment
6. **Review UI** — Court Desk, Review Queue, Evidence Room

> Not included in this POC: WhisperX, MediaPipe, OPA, Vault, Keycloak, credentials, TPN, full 8-axis scoring.

---

## Quick start (local)

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

### 3. Smoke test with bundled sample (no movie needed)

```bash
python scripts/demo_ingest.py
```

Then open the URL printed in the terminal.

---

## Test on a released movie (your files)

Use a **short clip** (5–15 min), not a full 2-hour film, for the first run.

### What you need

| File | Required | Purpose |
|------|----------|---------|
| `.srt` subtitles for the dubbed version | Yes | Creates segments + dialogue text |
| Video `.mp4` / `.mkv` OR audio `.wav` | Recommended | Sync + performance scoring |
| Original script `.txt` | Optional | Semantic comparison (source vs dub) |

### Option A — Web upload (easiest)

1. Go to **http://localhost:3000/ingest**
2. Enter title name and languages (e.g. `te` → `hi`)
3. Upload SRT + video/audio + optional script
4. Click **Submit for Scoring**
5. Open the title → review flagged segments in **Evidence Room**

### Option B — Local file paths

If files are already on disk (same machine as backend):

```bash
curl -X POST http://localhost:8000/api/v1/titles/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "title_name": "My Movie Hindi Dub Clip",
    "language": "hi",
    "source_language": "te",
    "video_path": "/absolute/path/to/clip.mp4",
    "srt_path": "/absolute/path/to/subtitles.srt",
    "script_path": "/absolute/path/to/script.txt"
  }'
```

### Extract a clip from a released movie (your machine)

```bash
# 5-minute clip starting at 00:10:00
ffmpeg -ss 00:10:00 -t 00:05:00 -i "/path/to/movie.mp4" -c copy clip.mp4

# Extract audio for scoring
ffmpeg -i clip.mp4 -vn -acodec pcm_s16le -ar 16000 clip.wav
```

Use only content you have the legal right to use for testing.

---

## What the POC scores

| Check | How it works in POC |
|-------|---------------------|
| **Semantic** | Compares script line vs dubbed subtitle (RapidFuzz; optional ML model) |
| **Sync** | Audio energy peak vs subtitle midpoint (librosa) |
| **Performance** | Energy / zero-crossing heuristics on audio clip |
| **Consent gate** | Fails if speaker label starts with `BLOCKED` |
| **Rights gate** | Fails if title name contains `UNLICENSED` |

Segments with utility **≥ 75** → `ACCEPTED`  
Between **50–75** → `FLAGGED` (human review)  
Below **50** → `REJECTED`

---

## Optional: better semantic scoring

Install ML model (downloads ~400MB on first run):

```bash
pip install sentence-transformers torch
export ENABLE_ML_SEMANTIC=true
```

---

## Docker

```bash
docker compose up --build
```

- API: http://localhost:8000/docs  
- UI: http://localhost:3000

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/dashboard` | Court Desk stats |
| POST | `/api/v1/titles/ingest` | Ingest by file paths |
| POST | `/api/v1/titles/ingest/upload` | Ingest by file upload |
| GET | `/api/v1/titles/{id}` | Title + all segments |
| GET | `/api/v1/titles/{id}/review-queue` | Flagged segments |
| POST | `/api/v1/segments/{id}/decision` | Accept / reject |

---

## Project layout

```
backend/          FastAPI scoring engine
frontend/         Next.js Court Desk + Evidence Room
fixtures/         Sample SRT + script for smoke test
scripts/          demo_ingest.py helper
```

---

## Next steps toward full CineWeave

- WhisperX forced alignment + MediaPipe lip drift
- OPA hard gates (spec, rights, consent from database)
- Decision memory (pgvector RAG)
- RS256 credentials + delivery gate
- Keycloak auth + studio isolation
