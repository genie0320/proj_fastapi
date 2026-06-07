from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.databases import Base
from app.core.db.models import UUIDMixin, TimestampMixin


class MedicalRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "medical_records"

    patient_uuid: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("patients.uuid", ondelete="CASCADE"),
        nullable=False
    )
    diagnosis: Mapped[str] = mapped_column(String(255), nullable=False)
    treatment: Mapped[str] = mapped_column(String(255), nullable=False)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="medical_records")
