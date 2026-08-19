import logging
import contextlib

from aioboto3 import Session
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router
from app.config import settings
from app.dependencies.db import engine
from app.models.base import Base
from app.services.s3_storage import S3StorageService

logger = logging.getLogger(__name__)


# Создание таблиц (в реальном проекте используйте Alembic)
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    aioboto3_session = Session()

    async with aioboto3_session.client(
        service_name="s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
    ) as s3_client:
        storage = S3StorageService(client=s3_client, bucket=settings.S3_BUCKET)
        await storage.ensure_bucket()
        app.state.storage = storage
        logger.info("S3 storage initialized: bucket=%s", settings.S3_BUCKET)

        yield

    logger.info("S3 storage closed")


app = FastAPI(title="Auth Demo", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok"}
