# CineWeave RAE

Governance scoring proof-of-concept for dubbed film content.

Score a short dubbed clip, review flagged segments, and see how CineWeave works end-to-end.

```
cineweave-rae/
├── backend/              FastAPI scoring engine
├── frontend/             Next.js Court Desk + Evidence Room
├── test-media/
│   ├── pushpa/           Your test movie files go here
│   └── uploads/          Auto-stored ingested files
├── fixtures/             Built-in sample SRT for smoke test
├── scripts/              Setup and start scripts
├── .env.example          Copy to .env
└── package.json          Root npm scripts
```

---

## Quick start (5 minutes)

### 1. Setup (first time only)

```bash
chmod +x scripts/*.sh
./scripts/setup.sh
```

### 2. Add your test files

Place your Pushpa clip in `test-media/pushpa/`:

| File | Required |
|------|----------|
| `pushpa_apology.srt` | Yes |
| `pushpa_apology.mp4` | Recommended |
| `pushpa_apology.mp3` | Optional |

Use simple filenames (no emojis or special characters).

### 3. Start the app

```bash
./scripts/start-all.sh
```

Or in two terminals:

```bash
./scripts/start-backend.sh    # Terminal 1 — port 8000
./scripts/start-frontend.sh   # Terminal 2 — port 3000
```

### 4. Verify backend

Open: http://127.0.0.1:8000/api/v1/health

Must show: `{"status":"ok","service":"cineweave-rae"}`

### 5. Ingest and score

**Web UI:** http://localhost:3000/ingest

**Or CLI** (if files are in `test-media/pushpa/`):

```bash
./scripts/ingest-pushpa.sh
```

### 6. Review results

- **Court Desk:** http://localhost:3000
- **Flagged segments:** open title → Evidence Room

---

## What this POC does

| Step | Description |
|------|-------------|
| Ingest | Accepts video/audio + SRT (+ optional script) |
| Segment | One subtitle cue = one review segment |
| Hard gates | Consent, rights, spec (POC stubs) |
| Soft scores | Semantic, sync timing, performance |
| Verdict | ACCEPTED / FLAGGED / REJECTED per segment |
| Review | Human accept/reject in Evidence Room |

**Not in this POC:** WhisperX, MediaPipe, OPA, Vault, Keycloak, credentials, TPN.

---

## Troubleshooting

### `ERR_CONNECTION_REFUSED` on localhost:3000

Frontend not started. Run `./scripts/start-frontend.sh`.

### `Failed to fetch` or `Backend not connected`

Backend not started. Run `./scripts/start-backend.sh`.

Verify: http://127.0.0.1:8000/api/v1/health

### `uvicorn: command not found`

Use:

```bash
PYTHONPATH=backend python3 -m uvicorn app.main:app --reload --port 8000
```

(from inside `backend/` directory)

### Health works but ingest page says not connected

Restart frontend after `git pull`:

```bash
cd frontend && npm run dev
```

Hard refresh browser: **Ctrl+Shift+R**

---

## Environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8000` | Frontend → backend URL |
| `MEDIA_ROOT` | `./test-media/uploads` | Stored uploads |
| `ENABLE_ML_SEMANTIC` | `false` | Use sentence-transformers |

---

## Docker (optional)

```bash
docker compose up --build
```

- API docs: http://localhost:8000/docs
- UI: http://localhost:3000

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/dashboard` | Court Desk stats |
| POST | `/api/v1/titles/ingest` | Ingest by file paths |
| POST | `/api/v1/titles/ingest/upload` | Ingest by file upload |
| GET | `/api/v1/titles/{id}` | Title + segments |
| POST | `/api/v1/segments/{id}/decision` | Accept / reject |

---

## Rename from Demo_repo

If you cloned the old `Demo_repo`:

```bash
git clone -b cursor/cineweave-rae-clean-a550 \
  https://github.com/satish-999/Demo_repo.git cineweave-rae
cd cineweave-rae
./scripts/setup.sh
```

Optionally rename the GitHub repository to `cineweave-rae` in GitHub Settings.

---

## License

Private / engineering use. CineWeave RAE POC.
