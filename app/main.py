from fastapi import FastAPI
from app.routers.health import router as health_router
from app.routers.plays import router as plays_router
from pathlib import Path
import os
from app.repositories.sqlite import SQLitePlaysRepo

app = FastAPI()

@app.on_event("startup")
def setup_repo():
    db_path = Path(os.getenv("DB_PATH", "./var/app.db")) 
    app.state.repo = SQLitePlaysRepo(db_path)

app.include_router(health_router)
app.include_router(plays_router)