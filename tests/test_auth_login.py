async def test_login_returns_token_and_cookie(client, register_confirmed_user):
    await register_confirmed_user(email="user@example.com", password="secret123")

    response = await client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "secret123"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert "access_token" in response.cookies


async def test_login_with_wrong_password_returns_403(client, register_confirmed_user):
    await register_confirmed_user(email="user@example.com", password="secret123")

    response = await client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "wrong-pass"},
    )

    assert response.status_code == 403


async def test_login_with_unknown_email_returns_401(client):
    response = await client.post(
        "/api/auth/login",
        json={"email": "ghost@example.com", "password": "secret123"},
    )

    assert response.status_code == 401


async def test_logout_clears_cookie(client, register_confirmed_user):
    await register_confirmed_user()

    response = await client.post("/api/auth/logout")

    assert response.status_code == 200
    me = await client.get("/api/user/me")
    assert me.status_code == 401
