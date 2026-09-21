import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import Depends
from fastapi.templating import Jinja2Templates
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings as st
from share.clients.database import get_database
from share.services.cache import CacheService
from share.services.email import EmailService
from users.models import User
from users.repository import UserRepository
from users.schemas import UserCreateS, UserDisplayS

from . import exceptions as exc
from .repository import UserPasswordRepository
from .schemas import AccessTokenDisplayS, UserAuthDisplayS, UserAuthS

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


class AuthService:
    database_client: AsyncSession
    cache_service: CacheService
    email_service: EmailService

    @classmethod
    def get_service(
        cls,
        database_client: AsyncSession = Depends(get_database),
        cache_service: CacheService = Depends(CacheService.get_service),
        email_service: EmailService = Depends(EmailService.get_service),
    ) -> "AuthService":
        service = cls()
        service.database_client = database_client
        service.cache_service = cache_service
        service.email_service = email_service
        return service

    async def register_user(self, user: UserCreateS) -> None:
        if await UserRepository.get(self.database_client, email=user.email):
            raise exc.USER_EXIST

        session_id = uuid4()
        await self.cache_service.set(
            key=f"register:{session_id}",
            value=user.model_dump_json(),
            ex=st.REGISTER_SESSION_TTL,
        )

        html = templates.env.get_template("email_register.html").render(
            {
                "app_name": st.SMTP_FROM_NAME,
                "confirm_url": (
                    f"{st.BE_URL}/api/auth/register/confirm?session_id={session_id}"
                ),
                "email": user.email,
                "current_year": datetime.now().year,
            }
        )
        self.email_service.send_email(
            message=html, to_email=user.email, subject="Подтверждение регистрации"
        )

    async def confirm_user_registration(self, session_id: UUID) -> UserAuthDisplayS:
        cache_key = f"register:{session_id}"
        payload = await self.cache_service.get(key=cache_key)
        if not payload:
            raise exc.SESSION_EXPIRED
        await self.cache_service.delete(cache_key)

        user = UserCreateS.model_validate_json(payload)
        if await UserRepository.get(self.database_client, email=user.email):
            raise exc.USER_EXIST

        user_db = await UserRepository.add(
            connection=self.database_client, email=user.email
        )
        await UserPasswordRepository.add(
            connection=self.database_client,
            user_id=user_db.id,
            password=self.get_password_hash(user.password),
        )

        user_sch = UserDisplayS(id=user_db.id, email=user_db.email)
        access_token = self.create_access_token(user_sch)
        return UserAuthDisplayS(user=user_sch, access_token=access_token)

    async def login_user(self, user: UserAuthS) -> str:
        user_db = await self.authenticate_user(user.email, user.password)
        user_sch = UserDisplayS(id=user_db.id, email=user_db.email)
        return self.create_access_token(user_sch)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_pass, hashed_pass) -> bool:
        return pwd_context.verify(plain_pass, hashed_pass)

    def create_access_token(self, data: UserDisplayS) -> str:
        to_encode = data.to_dict()
        expire = datetime.now(timezone.utc) + timedelta(hours=st.TOKEN_EXPIRE_HOURS)
        to_encode.update({"exp": expire})
        to_encode["sub"] = str(to_encode.get("id"))
        del to_encode["id"]
        return jwt.encode(to_encode, st.SECRET, st.HASH)

    def check_access_token(self, payload: AccessTokenDisplayS):
        expire = payload.exp
        if not expire or int(expire) < datetime.now().timestamp():
            raise exc.TOKEN_TIME_NOT_VALID

        if not payload.sub:
            raise exc.TOKEN_ID_NOT_VALID

        if not payload.email:
            raise exc.TOKEN_EMAIL_NOT_VALID

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await UserRepository.get(self.database_client, email=email)
        if not user:
            raise exc.USER_DOES_NOT_EXIST

        user_password = await UserPasswordRepository.get(
            self.database_client, user_id=user.id
        )
        if not user_password:
            raise exc.USER_DOES_NOT_EXIST

        if not self.verify_password(password, user_password.password):
            raise exc.NOT_VALID_PASS

        return user
