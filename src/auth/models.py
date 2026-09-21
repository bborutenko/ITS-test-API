import uuid as ui

from sqlalchemy import UUID, VARCHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from share.clients.database import Base


class UserPassword(Base):
    __tablename__ = "users_passwords"

    id: Mapped[ui.UUID] = mapped_column(UUID, primary_key=True)
    user_id: Mapped[ui.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    password: Mapped[str] = mapped_column(VARCHAR(70), nullable=False)

    user = relationship("User", back_populates="info")
