from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from app.models.user import User
from app.schemas import UserAvatar, UserResponse
from app.services.s3_storage import ObjectNotFoundError, S3StorageService, StorageError

ALLOWED_USER_AVATAR_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 Mbytes


async def upload_user_avatar(
    user: User, upload_file: UploadFile, storage: S3StorageService, db: AsyncSession
) -> UserResponse:
    if upload_file.content_type not in ALLOWED_USER_AVATAR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG and WEBP are allowed",
        )

    data = await upload_file.read()

    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only files no more than 10 MB are allowed",
        )

    file_key = storage.build_key(
        prefix="user/avatar",
        owner_id=user.id,
        filename=upload_file.filename or "avatar.jpg",
    )

    try:
        await storage.upload(
            key=file_key, data=data, content_type=upload_file.content_type
        )
    except StorageError:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="S3 storage file uploading failed",
        )

    old_key = user.avatar_key

    if old_key:
        try:
            await storage.delete(old_key)
        except Exception:
            pass

    user.avatar_key = file_key
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


async def get_user_avatar_url(avatar_key: str, storage: S3StorageService) -> UserAvatar:
    try:
        url = await storage.presigned_get_url(key=avatar_key)
        return UserAvatar(url=url)
    except ObjectNotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    except Exception:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR)


async def get_user(user_id: int, db: AsyncSession) -> UserResponse:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            HTTP_404_NOT_FOUND, detail="User with provided ID not found"
        )
    return UserResponse.model_validate(user)
