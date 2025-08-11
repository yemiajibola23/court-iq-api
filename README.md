# Court IQ API (FastAPI)

Thin backend for the CourtIQ app. v0 includes a health check and a minimal “create play” endpoint; next slices add Firestore, background processing, and Storage.

## Requirements
- Python **3.12** (recommended via `pyenv 3.12.5`)
- pip / venv
- (Soon) Firebase Emulator Suite for local Firestore/Storage testing

## Quick start

```bash
git clone <your-repo-url> court-iq-api
cd court-iq-api

# Python 3.12 virtual env
python3.12 -m venv .venv
source .venv/bin/activate

# Install deps
pip install --upgrade pip
pip install -r requirements.txt

# Run tests
pytest -q

# Run the dev server
uvicorn app.main:app --reload --port 8000
# Visit http://localhost:8000/health
```

## Endpoints (v0)
- `GET /health` → `{"ok": true}`
- `POST /v1/plays` → `{"playId": "<uuid>"}`  
  _Body_: `{"title": "Test Play", "video_path": "gs://bucket/plays/demo/raw.mp4"}`

> Note: v0 returns a UUID only; Firestore persistence and background processing land in the next slice.

## Project structure

```
app/
  main.py            # FastAPI app + routes (health, create play v0)
tests/
  test_health.py     # health + create play test
requirements.txt
pytest.ini           # adds repo root to PYTHONPATH
```

## Dev scripts (suggested)
You can use these one-liners or add a `Makefile` later:

```bash
# start dev
uvicorn app.main:app --reload --port 8000

# run tests
pytest -q
```

## Python version pin
This project targets **Python 3.12** because `pydantic-core`’s Rust binding (PyO3) lags on 3.13.

- If you use **pyenv**, create `.python-version` with:
  ```
  3.12.5
  ```
  I recommend **committing** this file so everyone uses a compatible version.

- If you prefer not to enforce a version, add `.python-version` to `.gitignore`.

## Next steps (Slice 1 → 2)
- Add Pydantic models (`PlayDoc`, `CreatePlayRequest`).
- Wire **Firestore (emulator)**: write `plays/{id}` on create.
- Add a tiny background worker (thread) that flips `status: processing → complete`.
- Expose `GET /v1/plays/{id}` to fetch the doc/status.
- (Slice 2) Add ffmpeg frame extraction and save thumbnails to Storage (emulator).

## Troubleshooting

- **Module import error in tests**  
  Make sure `pytest.ini` contains:
  ```ini
  [pytest]
  pythonpath = .
  ```

- **Pydantic build error on 3.13**  
  Use Python **3.12.x** (e.g., `pyenv local 3.12.5`), recreate `.venv`, reinstall deps.
