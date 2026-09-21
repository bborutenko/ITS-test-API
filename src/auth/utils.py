from fastapi import Depends, Request
from jose import JWTError, jwt

from config.settings import settings as st
from users.models import User
from users.repository import UserRepository

from . import exceptions as exc
from .schemas import AccessTokenDisplayS
from .service import AuthService


def get_token(
    request: Request,
) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise exc.USER_NOT_AUTHORIZED
    return token


async def get_current_user(
    token: str = Depends(get_token),
    service: AuthService = Depends(AuthService.get_service),
) -> User:
    try:
        payload = jwt.decode(token, st.SECRET, st.HASH)
    except JWTError:
        raise exc.USER_NOT_AUTHORIZED

    try:
        token_data = AccessTokenDisplayS(**payload)
    except Exception:
        raise exc.USER_NOT_AUTHORIZED

    service.check_access_token(token_data)

    user = await UserRepository.get(service.database_client, id=token_data.sub)
    if not user:
        raise exc.USER_DOES_NOT_EXIST

    return user
