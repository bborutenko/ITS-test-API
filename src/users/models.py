import uuid as ui

from sqlalchemy import UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from share.clients.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[ui.UUID] = mapped_column(UUID, primary_key=True)
    email: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)

    info = relationship("UserPassword", back_populates="user")
