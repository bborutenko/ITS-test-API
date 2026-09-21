from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException
from jose import JWTError, jwt

from auth.schemas import AccessTokenDisplayS
from auth.service import AuthService
from config.settings import settings as st
from users.schemas import UserDisplayS


def test_create_and_check_access_token():
    service = AuthService()
    user = UserDisplayS(id=uuid4(), email="user@example.com")

    token = service.create_access_token(user)

    payload = AccessTokenDisplayS(**jwt.decode(token, st.SECRET, st.HASH))
    service.check_access_token(payload)
    assert str(payload.sub) == str(user.id)
    assert payload.email == user.email


def test_check_access_token_rejects_expired():
    service = AuthService()
    expired = AccessTokenDisplayS(
        exp=int((datetime.now() - timedelta(hours=1)).timestamp()),
        sub=uuid4(),
        email="user@example.com",
    )

    with pytest.raises(HTTPException) as err:
        service.check_access_token(expired)

    assert err.value.status_code == 401


def test_decode_rejects_expired_jwt():
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "email": "user@example.com",
            "exp": int(datetime.now().timestamp()) - 3600,
        },
        st.SECRET,
        st.HASH,
    )

    with pytest.raises(JWTError):
        jwt.decode(token, st.SECRET, st.HASH)
