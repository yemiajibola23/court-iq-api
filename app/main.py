from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.models.errors import install_422_handlers
from app.repositories.memory import MemoryRepository
from app.routers.health import router as health_router
from app.routers.plays import router as plays_router

@asynccontextmanager
async def lifespan(app: FastAPI):
   try:
       MemoryRepository().clear()  # if you want a clean slate in dev
   except Exception:
       pass
   yield

app = FastAPI(lifespan=lifespan)
install_422_handlers(app)

app.include_router(health_router)
app.include_router(plays_router)