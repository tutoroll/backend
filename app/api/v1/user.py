from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.dependencies.user import get_current_user
from app.models.user import User
from app.schemas import UserResponse
from app.services.user import get_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_user(user_id=user_id, db=db)


@router.get("/me", response_model=UserResponse)
async def get_cur_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user)
