import os

import redis.asyncio as aioredis

from conftest import extract_session_id


async def redis_keys(pattern: str) -> list[str]:
    cache = aioredis.from_url(os.environ["CACHE_URL"], decode_responses=True)
    try:
        return await cache.keys(pattern)
    finally:
        await cache.aclose()


async def test_register_with_invalid_email_returns_422(client, email_spy):
    response = await client.post(
        "/api/auth/register", json={"email": "not-an-email", "password": "secret123"}
    )

    assert response.status_code == 422
    assert email_spy == []


async def test_register_sends_confirmation_email_and_stores_session(client, email_spy):
    response = await client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "secret123"},
    )

    assert response.status_code == 201
    assert response.json() == {"ok": True}

    assert len(email_spy) == 1
    call = email_spy[0]
    assert call["to_email"] == "user@example.com"
    assert call["subject"] == "Подтверждение регистрации"
    assert "session_id=" in call["message"]

    keys = await redis_keys("register:*")
    assert len(keys) == 1


async def test_register_existing_user_returns_400(client, register_confirmed_user):
    await register_confirmed_user(email="user@example.com")

    response = await client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "another-pass"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "User is already exist"
