async def test_me_without_cookie_returns_401(client):
    response = await client.get("/api/user/me")

    assert response.status_code == 401


async def test_me_with_garbage_token_returns_401(client, register_confirmed_user):
    await register_confirmed_user()

    client.cookies.set("access_token", "garbage.token.value")
    response = await client.get("/api/user/me")

    assert response.status_code == 401


async def test_health(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
