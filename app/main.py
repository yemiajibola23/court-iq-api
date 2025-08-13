from fastapi import FastAPI, APIRouter
from app.routers.health import router as health_router

app = FastAPI()

app.include_router(health_router)