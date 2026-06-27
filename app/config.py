from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    COOKIE_DOMAIN: str = "localhost"           # для production замените на свой домен
    COOKIE_SECURE: bool = True                # True в production (HTTPS), False - для локальной разработки
    COOKIE_SAMESITE: str = "lax"

    class Config:
        env_file = ".env"

settings = Settings()