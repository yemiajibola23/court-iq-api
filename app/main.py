from fastapi import FastAPI, APIRouter
from app.routers.health import router as health_router
from app.routers.plays import router as plays_router
app = FastAPI()

app.include_router(health_router)
app.include_router(plays_router)