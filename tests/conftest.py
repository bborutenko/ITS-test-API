import asyncio
import atexit
import os
import re

import pytest
import pytest_asyncio
import redis.asyncio as aioredis
from httpx import ASGITransport, AsyncClient
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer

os.environ.setdefault("TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", "/var/run/docker.sock")

postgres = PostgresContainer(
    "postgres:16-alpine", username="test", password="test", dbname="test"
)
redis_container = RedisContainer("redis:7-alpine")

postgres.start()
redis_container.start()
atexit.register(postgres.stop)
atexit.register(redis_container.stop)

os.environ["DATABASE_URL"] = (
    f"postgresql://{postgres.username}:{postgres.password}"
    f"@{postgres.get_container_host_ip()}:{postgres.get_exposed_port(5432)}"
    f"/{postgres.dbname}"
)
os.environ["CACHE_URL"] = (
    f"redis://{redis_container.get_container_host_ip()}"
    f":{redis_container.get_exposed_port(6379)}/0"
)
os.environ["SECRET"] = "test-secret"
os.environ.pop("COOKIE_DOMAIN", None)
os.environ.pop("COOKIE_SECURE", None)

CONFIRM_URL_RE = re.compile(r"session_id=([0-9a-fA-F-]{36})")


def extract_session_id(email_html: str) -> str:
    match = CONFIRM_URL_RE.search(email_html)
    assert match, f"confirm link not found in email: {email_html!r}"
    return match.group(1)


@pytest.fixture(scope="session", autouse=True)
def _run_migrations():
    from config.alembic import upgrade_all_migrations

    upgrade_all_migrations()


@pytest.fixture(autouse=True)
def clean_storage():
    from share.clients.database import Base, engine

    async def _clean():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        cache = aioredis.from_url(os.environ["CACHE_URL"], decode_responses=True)
        try:
            await cache.flushdb()
        finally:
            await cache.aclose()

    asyncio.run(_clean())


@pytest.fixture(autouse=True)
def email_spy(monkeypatch):
    from share.services.email import EmailService

    calls: list[dict] = []

    def _fake_send(self, message: str, to_email: str, subject: str) -> None:
        calls.append({"message": message, "to_email": to_email, "subject": subject})

    monkeypatch.setattr(EmailService, "send_email", _fake_send)
    return calls


@pytest_asyncio.fixture
async def client():
    from main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture
async def register_confirmed_user(client, email_spy):
    async def _register(email: str = "user@example.com", password: str = "secret123"):
        response = await client.post(
            "/api/auth/register", json={"email": email, "password": password}
        )
        assert response.status_code == 201, response.text

        session_id = extract_session_id(email_spy[-1]["message"])
        response = await client.get(
            "/api/auth/register/confirm", params={"session_id": session_id}
        )
        assert response.status_code == 303, response.text
        return {"email": email, "password": password}

    return _register
