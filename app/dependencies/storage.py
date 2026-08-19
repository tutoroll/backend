from fastapi import Request

from app.services.s3_storage import S3StorageService

def get_storage(request: Request) -> S3StorageService:
    storage = getattr(request.app.state, "storage", None)
    if storage is None:
        raise RuntimeError("Storage is not initialized")
    return storage