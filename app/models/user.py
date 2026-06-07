from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.databases import Base
from app.core.db.models import UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="Waiting", server_default="Waiting", nullable=False)

    def __repr__(self) -> str:
        return f"<User(uuid={self.uuid}, email='{self.email}', role='{self.role}')>"
