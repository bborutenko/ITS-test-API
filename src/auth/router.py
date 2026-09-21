from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings as st
from share.clients.database import get_database
from users.schemas import UserCreateS

from . import schemas as sch
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["Authorization"])


@router.post(path="/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreateS,
    service: AuthService = Depends(AuthService.get_service),
    connection: AsyncSession = Depends(get_database),
) -> dict[str, bool]:
    await service.register_user(user)
    await connection.commit()
    return {"ok": True}


@router.get(path="/register/confirm", status_code=status.HTTP_303_SEE_OTHER)
async def confirm_register_user(
    session_id: UUID,
    service: AuthService = Depends(AuthService.get_service),
    connection: AsyncSession = Depends(get_database),
) -> Response:
    result = await service.confirm_user_registration(session_id)
    await connection.commit()

    redirect = RedirectResponse(
        url="/api/auth/register/success",
        status_code=status.HTTP_303_SEE_OTHER,
    )
    redirect.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=st.COOKIE_SECURE,
        domain=st.COOKIE_DOMAIN,
        path="/",
    )
    return redirect


@router.get(path="/register/success", status_code=status.HTTP_200_OK)
async def register_success_page(request: Request) -> Response:
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request, name="registration_success.html"
    )


@router.post("/login")
async def login_user(
    response: Response,
    user: sch.UserAuthS,
    service: AuthService = Depends(AuthService.get_service),
) -> dict[str, str]:
    access_token = await service.login_user(user)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=st.COOKIE_SECURE,
        domain=st.COOKIE_DOMAIN,
        path="/",
    )
    return {"access_token": access_token}


@router.post("/logout")
async def log_out_user(
    response: Response,
) -> dict[str, str]:
    response.delete_cookie(
        key="access_token",
        domain=st.COOKIE_DOMAIN,
        path="/",
        httponly=True,
        secure=st.COOKIE_SECURE,
    )
    return {"message": "ok"}
