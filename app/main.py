from fastapi import FastAPI, APIRouter
import uuid

app = FastAPI()
api = APIRouter(prefix="/v1")

@app.get("/health")
def health():
    return {"ok": True}

@api.post("/plays")
def create_play(payload: dict):
    # TODO: - Validate with pydantic
    _ = payload.get("title"), payload.get("video_path")
    return {"playId": str(uuid.uuid4())}

app.include_router(api)