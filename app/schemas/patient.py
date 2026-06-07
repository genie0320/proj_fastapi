from datetime import datetime
from uuid import UUID
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class PatientBase(BaseModel):
    name: str = Field(..., max_length=100, description="Patient full name")
    age: int = Field(..., ge=0, description="Patient age in years")
    phone_number: str = Field(..., max_length=50, description="Patient contact phone number")
    gender: str = Field(..., max_length=20, description="Patient gender")


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100, description="Updated patient name")
    phone_number: str | None = Field(default=None, max_length=50, description="Updated contact phone number")


class PatientResponse(PatientCreate):
    uuid: UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PatientDetailResponse(PatientResponse):
    medical_records: list[dict[str, Any]] = Field(
        default=[],
        description="Mocked medical records for frontend contract alignment"
    )
