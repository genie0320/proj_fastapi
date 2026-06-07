from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.databases import Base
from app.core.db.models import UUIDMixin, TimestampMixin


class Patient(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "patients"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)

    # Cascading delete configuration to avoid FK constraints violations (REQ-PTNT-005)
    medical_records: Mapped[list["MedicalRecord"]] = relationship(
        "MedicalRecord",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Patient(uuid={self.uuid}, name='{self.name}')>"
