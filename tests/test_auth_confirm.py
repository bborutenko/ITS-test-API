from uuid import uuid4

from conftest import extract_session_id


async def register_user(client, email="user@example.com", password="secret123"):
    response = await client.post(
        "/api/auth/register", json={"email": email, "password": password}
    )
    assert response.status_code == 201, response.text
    return response


async def test_confirm_link_authorizes_user(client, email_spy):
    await register_user(client)
    session_id = extract_session_id(email_spy[0]["message"])

    response = await client.get(
        "/api/auth/register/confirm", params={"session_id": session_id}
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/api/auth/register/success"
    assert "access_token" in response.cookies

    me = await client.get("/api/user/me")
    assert me.status_code == 200
    assert me.json()["email"] == "user@example.com"


async def test_confirm_link_is_one_time(client, email_spy):
    await register_user(client)
    session_id = extract_session_id(email_spy[0]["message"])

    first = await client.get(
        "/api/auth/register/confirm", params={"session_id": session_id}
    )
    second = await client.get(
        "/api/auth/register/confirm", params={"session_id": session_id}
    )

    assert first.status_code == 303
    assert second.status_code == 400


async def test_confirm_with_unknown_session_id_returns_400(client):
    response = await client.get(
        "/api/auth/register/confirm", params={"session_id": str(uuid4())}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Confirmation link is invalid or expired"


async def test_success_page_renders(client):
    response = await client.get("/api/auth/register/success")

    assert response.status_code == 200
    assert "Registration successful" in response.text
