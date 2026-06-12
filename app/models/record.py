import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.databases import Base
from app.core.db.models import UUIDMixin, TimestampMixin


class MedicalRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "medical_records"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.uuid"), nullable=False
    )
    chart_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)

    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="medical_records"
    )

    def __repr__(self) -> str:
        return f"<MedicalRecord(uuid={self.uuid}, chart_number='{self.chart_number}', patient_id={self.patient_id})>"
