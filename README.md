## Tutoroll Backend

The backend service for Tutoroll built with `FastAPI`. This repository is responsible for authentication, user profile APIs, and avatar storage via an S3-compatible object storage.

## Implemented Features

- user registration;
- login with `HttpOnly` cookie-based `access_token` and `refresh_token`;
- access token refresh via refresh token;
- logout with refresh token revocation;
- current user retrieval;
- avatar upload and avatar URL retrieval;
- local development stack via `docker-compose` with `PostgreSQL` and `MinIO`.

## Project Structure

- `app/api/v1/` - HTTP routes (`/auth`, `/user`);
- `app/services/` - business logic for auth, users, and S3 storage;
- `app/models/` - SQLAlchemy models;
- `app/schemas/` - Pydantic request/response schemas;
- `app/dependencies/` - FastAPI dependencies for DB, current user, and storage;
- `main.py` - application entry point, CORS setup, and lifecycle wiring.

## Tech Stack

- `Python 3.14`
- `FastAPI`
- `SQLAlchemy 2`
- `asyncpg`
- `Pydantic v2` + `pydantic-settings`
- `python-jose` for JWT
- `passlib` + `bcrypt` for password hashing
- `aioboto3` / S3 API
- `PostgreSQL`
- `MinIO` for local S3-compatible storage
- `uv` for dependency management

## API

### Auth

- `POST /auth/register` - register a new user
- `POST /auth/login` - sign in
- `POST /auth/refresh` - refresh access token
- `POST /auth/logout` - sign out

### User

- `GET /user/me` - get current user
- `GET /user/{user_id}` - get user by ID
- `POST /user/avatar/me` - upload current user avatar
- `GET /user/avatar/me` - get current user avatar URL
- `GET /user/avatar/{avatar_key}` - get avatar URL by key

## Environment Variables

See `.env.example` for a full configuration template.

Required variables:

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

## Local Run

### Option 1: Docker Compose

```bash
docker compose up --build
```

This starts:

- backend at `http://localhost:8000`
- PostgreSQL at `localhost:5432`
- MinIO S3 API at `http://localhost:9000`
- MinIO console at `http://localhost:9001`

### Option 2: Local run with uv

```bash
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A local `.env` file is required.

## Implementation Notes

- access tokens are signed JWTs;
- refresh tokens are stored in the database as SHA-256 hashes;
- cookies are the main auth transport;
- on startup, the app initializes DB tables and S3 storage;
- in development, the MinIO bucket can be created automatically.

## Important Notes

- database tables are currently created from `SQLAlchemy metadata`; for production, use `Alembic` migrations;
- CORS is configured for local frontend origin `http://localhost:3000`;
- values in `.env.example` are placeholders and must not be used in production.
