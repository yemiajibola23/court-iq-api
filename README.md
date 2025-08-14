# CourtIQ API

Backend service for CourtIQ, providing endpoints for play creation, retrieval, and analysis.

## Tech Stack
- Python 3.12+
- FastAPI
- Pytest
- Firebase (optional for storage and authentication)

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
## API

### POST `/v1/plays`

Create a new play.

**Request body**
```json
{
  "title": "Spain PnR vs Drop",
  "video_path": "https://example.com/clip.mp4"
}
```
**Validation**
- `title`: required, non-empty (whitespace trimmed, 1–120 chars).
- `video_path`: required; must be http(s) URL or a valid file-like path (Unix abs /..., Windows abs C:\..., or relative ../...).

**Resposnse**
- 201 Created
- Headers: `Location /v1/plays/{id}`
- Body:
```json
{
  "playId": "2c8e0a09-8a6b-4b3b-8f6d-7d2e2e6f3f71"
}
```
**Examples**
HTTPie
```bash
http POST :8000/v1/plays title="Spain PnR vs Drop" \
  video_path="https://example.com/clip.mp4" -v
```

**curl**
```bash
curl -i -X POST http://127.0.0.1:8000/v1/plays \
  -H "Content-Type: application/json" \
  -d '{"title":"Spain PnR vs Drop","video_path":"https://example.com/clip.mp4"}'

```

**Validation error (422)**
```bash
http POST :8000/v1/plays title="  " video_path="https://example.com/clip.mp4"
```



## Contributing

We welcome contributions!  
Before you start, please read our [Contributing Guidelines](CONTRIBUTING.md) and the [Project Workflow](docs/WORKFLOW.md) to understand how we work and commit changes.

## Troubleshooting

- **Module import error in tests**  
  Make sure `pytest.ini` contains:

  ```ini
  [pytest]
  pythonpath = .
  ```

- **Pydantic build error on 3.13**  
  Use Python **3.12.x** (e.g., `pyenv local 3.12.5`), recreate `.venv`, reinstall deps.
