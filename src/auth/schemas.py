import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from users.schemas import UserDisplayS


class AccessTokenDisplayS(BaseModel):
    exp: int
    sub: UUID
    email: EmailStr

    def exp_datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.exp)


class UserAuthS(BaseModel):
    email: EmailStr
    password: str


class UserAuthDisplayS(BaseModel):
    user: UserDisplayS
    access_token: str
