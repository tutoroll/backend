from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.schemas import LoginUser, UserCreate, UserResponse
from app.services.auth import login, logout, refresh_tokens, register_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def regsiter(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(user_create=user_data, db=db)


@router.post("/login")
async def login_user(
    response: Response,
    login_model: LoginUser,
    db: AsyncSession = Depends(get_db),
):
    await login(response=response, login_model=login_model, db=db)


@router.post("/refresh")
async def refresh(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await refresh_tokens(response=response, request=request, db=db)


@router.post("/logout")
async def logout_user(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await logout(response=response, request=request, db=db)
