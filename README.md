## Tutoroll Backend

Backend-часть проекта Tutoroll на `FastAPI`. Репозиторий отвечает за аутентификацию пользователя, получение профиля и работу с аватарами через S3-совместимое хранилище.

## Что реализовано

- регистрация пользователя;
- логин с установкой `access_token` и `refresh_token` в `HttpOnly` cookies;
- обновление access token через refresh token;
- logout с отзывом refresh token;
- получение текущего пользователя;
- загрузка и получение ссылки на аватар;
- локальный dev-стенд через `docker-compose` с `PostgreSQL` и `MinIO`.

## Основные части проекта

- `app/api/v1/` - HTTP-роуты (`/auth`, `/user`);
- `app/services/` - бизнес-логика аутентификации, пользователей и S3-хранилища;
- `app/models/` - SQLAlchemy-модели;
- `app/schemas/` - Pydantic-схемы запросов и ответов;
- `app/dependencies/` - зависимости FastAPI для БД, текущего пользователя и storage;
- `main.py` - точка входа, инициализация приложения, CORS и lifecycle.

## Стек

- `Python 3.14`
- `FastAPI`
- `SQLAlchemy 2`
- `asyncpg`
- `Pydantic v2` + `pydantic-settings`
- `python-jose` для JWT
- `passlib` + `bcrypt` для хеширования паролей
- `aioboto3` / S3 API
- `PostgreSQL`
- `MinIO` для локального S3-совместимого хранилища
- `uv` для управления зависимостями

## API

### Auth

- `POST /auth/register` - регистрация пользователя
- `POST /auth/login` - вход
- `POST /auth/refresh` - обновление access token
- `POST /auth/logout` - выход

### User

- `GET /user/me` - текущий пользователь
- `GET /user/{user_id}` - пользователь по id
- `POST /user/avatar/me` - загрузка аватара
- `GET /user/avatar/me` - ссылка на аватар текущего пользователя
- `GET /user/avatar/{avatar_key}` - ссылка на аватар по ключу

## Переменные окружения

Пример конфигурации лежит в `.env.example`.

Обязательные переменные:

```env
SECRET_KEY=
COOKIE_SECURE=false
DATABASE_URL=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
S3_ENDPOINT=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET=
```

## Локальный запуск

### Вариант 1: через Docker Compose

```bash
docker compose up --build
```

Поднимутся:

- backend на `http://localhost:8000`
- PostgreSQL на `localhost:5432`
- MinIO S3 API на `http://localhost:9000`
- MinIO console на `http://localhost:9001`

### Вариант 2: локально через uv

```bash
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Перед запуском нужен файл `.env`.

## Особенности реализации

- access token подписывается через JWT;
- refresh token хранится в базе в виде SHA-256 хеша;
- cookies используются как основной транспорт для авторизации;
- при старте приложения создаются таблицы и инициализируется S3 storage;
- для development bucket в MinIO может создаваться автоматически.

## Что стоит учесть

- сейчас таблицы создаются из `SQLAlchemy metadata`; для production лучше использовать `Alembic` миграции;
- CORS настроен под локальный frontend на `http://localhost:3000`;
- значения в `.env.example` являются только примерами и не подходят для production.
