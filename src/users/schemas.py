from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreateS(BaseModel):
    email: EmailStr
    password: str


class UserDisplayS(BaseModel):
    id: UUID
    email: EmailStr

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
        }
