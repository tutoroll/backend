from fastapi import HTTPException, Request, Response, status
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from app.config import settings
import hashlib
import secrets

from app.models.auth import RefreshToken
from app.models.user import User
from app.schemas import LoginUser, UserCreate, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -----------Основная логика--------
async def register_user(user_create: UserCreate, db: AsyncSession) -> UserResponse:
    # проверка на пустые поля
    if (
        not user_create.email
        or not user_create.password
        or not user_create.name
        or not user_create.surname
    ):
        raise HTTPException(
            status_code=400,
            detail="Every of fields: email, password, name, surname must not be empty",
        )

    # проверка на существующего пользователя
    res = await db.execute(select(User).where(User.email == user_create.email))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already registered")

    # регистрация
    hashed_pass = get_password_hash(user_create.password)
    new_user = User(
        name=user_create.name,
        surname=user_create.surname,
        email=user_create.email,
        hashed_password=hashed_pass,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserResponse.model_validate(new_user)


async def login(response: Response, login_model: LoginUser, db: AsyncSession):
    # проверка на существующего пользователя
    res = await db.execute(select(User).where(User.email == login_model.email))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email/password")
    password_correct = verify_password(login_model.password, user.hashed_password)
    if not password_correct:
        raise HTTPException(status_code=400, detail="Invalid email/password")

    # access token
    access_token = create_access_token(data={"sub": str(user.id)})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        domain=settings.COOKIE_DOMAIN,
    )

    # refresh token
    create_and_set_new_refresh_token(response, db, user.id)
    await db.commit()


async def refresh_tokens(
    response: Response,
    request: Request,
    db: AsyncSession,
) -> None:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )

    token_hash = hash_refresh_token(refresh_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    token_record = result.scalar_one_or_none()
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = token_record.user_id

    # Токен валиден, создаём новый access
    new_access_token = create_access_token(data={"sub": str(user_id)})

    # Устанавливаем новый access в cookies
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        domain=settings.COOKIE_DOMAIN,
    )

    await revoke_refresh_token(request=request, db=db)
    create_and_set_new_refresh_token(response=response, db=db, user_id=user_id)
    await db.commit()


async def logout(
    response: Response,
    request: Request,
    db: AsyncSession,
):
    response.delete_cookie("access_token", domain=settings.COOKIE_DOMAIN)
    response.delete_cookie("refresh_token", domain=settings.COOKIE_DOMAIN)
    await revoke_refresh_token(request=request, db=db)


# -----------Работ с токенами------


def create_and_set_new_refresh_token(
    response: Response, db: AsyncSession, user_id: int
):
    raw_refresh_token = generate_refresh_token()
    token_hash = hash_refresh_token(raw_refresh_token)
    expires_at = create_refresh_token_expiry()

    # Сохраняем refresh-токен в БД
    new_refresh = RefreshToken(
        user_id=user_id, token_hash=token_hash, expires_at=expires_at, revoked=False
    )
    db.add(new_refresh)

    response.set_cookie(
        key="refresh_token",
        value=raw_refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        domain=settings.COOKIE_DOMAIN,
    )


async def revoke_refresh_token(request: Request, db: AsyncSession):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return
    ref_token_hash = hash_refresh_token(refresh_token)
    res = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == ref_token_hash)
    )
    ref_token_model = res.scalar_one_or_none()
    if not ref_token_model:
        return
    ref_token_model.revoked = True


# ---------- Пароли ----------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# ---------- JWT Access ----------
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError as e:
        print(e)
        return None


# ---------- Refresh токены (без JWT, генерируем случайную строку и храним хеш) ----------


def generate_refresh_token() -> str:
    # Генерируем случайную строку (64 символа)
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    # Хешируем токен для хранения в БД (SHA-256)
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )


def verify_refresh_token_hash(token: str, token_hash: str) -> bool:
    return hash_refresh_token(token) == token_hash
