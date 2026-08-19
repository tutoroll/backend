from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.dependencies.storage import get_storage
from app.dependencies.user import get_current_user
from app.models.user import User
from app.schemas import UserAvatar, UserResponse
from app.services.s3_storage import S3StorageService
from app.services.user import get_user, get_user_avatar_url, upload_user_avatar

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserResponse)
async def get_cur_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = current_user
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_user(user_id=user_id, db=db)


@router.post("avatar/me", response_model=UserResponse)
async def upload_avatar_for_current_user(
    file: UploadFile,
    storage: Annotated[S3StorageService, Depends(get_storage)],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await upload_user_avatar(
        user=current_user, storage=storage, db=db, upload_file=file
    )


@router.get("avatar/me", response_model=UserAvatar)
async def get_avatar_for_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
    storage: Annotated[S3StorageService, Depends(get_storage)],
):
    return await get_user_avatar_url(
        avatar_key=current_user.avatar_key, storage=storage
    )


@router.get("avatar/{avatar_key}", response_model=UserAvatar)
async def get_avatar_by_key(
    avatar_key: str,
    current_user: Annotated[User, Depends(get_current_user)],
    storage: Annotated[S3StorageService, Depends(get_storage)],
):
    return await get_user_avatar_url(avatar_key=avatar_key, storage=storage)
