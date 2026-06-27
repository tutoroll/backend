from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED

from app.dependencies.db import get_db
from app.models.user import User
from app.services.auth import decode_access_token


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(HTTP_401_UNAUTHORIZED)
    payload = decode_access_token(access_token)
    if not payload:
        raise HTTPException(HTTP_401_UNAUTHORIZED)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(HTTP_401_UNAUTHORIZED)
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(HTTP_401_UNAUTHORIZED)
    return user
