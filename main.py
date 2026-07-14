from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import contextlib

from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router
from app.dependencies.db import engine
from app.models.base import Base

app = FastAPI(title="Auth Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создание таблиц (в реальном проекте используйте Alembic)
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app.router.lifespan_context = lifespan

app.include_router(auth_router)
app.include_router(user_router)

@app.get("/")
async def root():
    return {"status": "ok"}