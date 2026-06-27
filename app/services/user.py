from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND
from app.models.user import User
from app.schemas import UserResponse


async def get_user(user_id: int, db: AsyncSession) -> UserResponse:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="User with provided ID not found")
    return UserResponse.model_validate(user)

