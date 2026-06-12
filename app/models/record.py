from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey

from app.core.db.databases import Base
from app.core.db.models import UUIDMixin, TimestampMixin
from datetime import datetime

class MedicalRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "medical_records"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.uuid"), nullable=False
    )
    chart_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationship (patients 테이블이 있을 경우)
    # patient = relationship("Patient", back_populates="medical_records")

    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, chart_number='{self.chart_number}', patient_id={self.patient_id})>"
