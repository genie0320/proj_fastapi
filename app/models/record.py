from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey

from app.core.db.databases import Base
from app.core.db.models import UUIDMixin, TimestampMixin
from datetime import datetime

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey("patients.id"), nullable=False)
    chart_number = Column(String(50), nullable=False, unique=True)
    symptoms = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Relationship (patients 테이블이 있을 경우)
    # patient = relationship("Patient", back_populates="medical_records")

    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, chart_number='{self.chart_number}', patient_id={self.patient_id})>"
