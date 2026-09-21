# ITS Test API

Регистрация с подтверждением email по ссылке: пользователь указывает email и пароль,
получает письмо со ссылкой, переходит по ней — и оказывается авторизованным в системе
(JWT в httpOnly-cookie).

## Стек

- **FastAPI** + uvicorn, Python 3.11+
- **PostgreSQL** — SQLAlchemy 2.0 (async) + asyncpg, миграции Alembic (прогоняются при старте)
- **Redis** — хранение pending-регистраций (`register:{session_id}`, TTL 10 минут)
- **Gmail SMTP** — отправка писем (App Password)
- **uv** — пакетный менеджер

## Архитектура

Доменная послойная структура: каждый домен (`auth`, `users`) содержит `router → service → repository → models → schemas`.
Сквозная инфраструктура в `share/` (клиенты БД/Redis, email-сервис, базовый репозиторий) и `config/` (настройки, программный запуск миграций).

```
src/
├── main.py                  # сборка приложения, роутеры, шаблоны
├── config/                  # settings (pydantic-settings), alembic-раннер
├── auth/                    # регистрация/подтверждение/логин, JWT, шаблоны писем
├── users/                   # User, GET /api/user/me
└── share/                   # get_database, get_cache, BaseRepository, EmailService, /health
deployment/
├── Dockerfile               # двухступенчатая сборка (uv)
└── docker-compose.yml       # api + postgres + redis
```

## Флоу авторизации

1. `POST /api/auth/register {email, password}` — валидация email (422), проверка уникальности (400),
   payload кладётся в Redis на 10 минут, на почту уходит письмо со ссылкой
   `{BE_URL}/api/auth/register/confirm?session_id=...`
2. `GET /api/auth/register/confirm?session_id=...` — переход по ссылке: сессия из Redis удаляется
   (ссылка одноразовая), создаются `users` + `users_passwords` (bcrypt), выдаётся JWT (3 часа)
   в httpOnly-cookie, редирект на страницу успеха. Пользователь авторизован.
3. `POST /api/auth/login {email, password}` — повторный вход, JWT + cookie.
4. `GET /api/user/me` — защищённый эндпоинт (проверка cookie через `get_current_user`).

## Запуск локально

```bash
cp .env.example .env      # заполнить SMTP (см. ниже)
uv sync
docker compose -f deployment/docker-compose.yml up -d postgres redis
uv run python src/main.py
```

Swagger: http://localhost:8000/docs

## Gmail App Password

1. Google Account → Security → включить 2-Step Verification
2. Security → App passwords → создать пароль для приложения
3. Вписать в `.env`:
   - `SMTP_USERNAME` / `SMTP_FROM` — ваш gmail-адрес
   - `SMTP_PASSWORD` — 16-символьный app password (без пробелов)

## Docker (полный стек)

```bash
cp .env.example .env
docker compose -f deployment/docker-compose.yml up --build
```

Поднимаются `api` (порт 8000), `postgres:16-alpine` (5432), `redis:7-alpine` (6379).
Миграции применяются автоматически при старте контейнера.

## Тесты

pytest + testcontainers: тестовое окружение само поднимает одноразовые Postgres и Redis
контейнеры, применяет миграции, чистит состояние перед каждым тестом. Отправка email мокается.

```bash
uv run pytest          # требуется запущенный Docker daemon
```
