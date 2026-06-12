# app/schemas/patient.py
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
import re
from app.models.patient import GenderEnum


class PatientBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=30)
    age: int = Field(..., ge=0, le=150)
    gender: GenderEnum
    phone: str = Field(..., min_length=10, max_length=11)

    @model_validator(mode="before")
    @classmethod
    def populate_phone(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "phone_number" in data and "phone" not in data:
                data["phone"] = data["phone_number"]
            if "gender" in data:
                gen = data["gender"]
                if isinstance(gen, str):
                    if gen.lower() in ["male", "m", "남성"]:
                        data["gender"] = GenderEnum.MALE
                    elif gen.lower() in ["female", "f", "여성"]:
                        data["gender"] = GenderEnum.FEMALE
        return data

    @field_validator("phone", mode="before")
    @classmethod
    def remove_hyphens_from_phone(cls, v: Any) -> Any:
        if isinstance(v, str):
            return re.sub(r"[- ]", "", v)
        return v


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=30)
    phone: Optional[str] = Field(None, min_length=10, max_length=11)

    @model_validator(mode="before")
    @classmethod
    def populate_phone(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "phone_number" in data and "phone" not in data:
                data["phone"] = data["phone_number"]
        return data

    @field_validator("phone", mode="before")
    @classmethod
    def remove_hyphens_from_phone(cls, v: Any) -> Any:
        if isinstance(v, str):
            return re.sub(r"[- ]", "", v)
        return v


class PatientListResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: GenderEnum
    phone: str
    created_at: datetime
    updated_at: Optional[datetime]

    @computed_field
    @property
    def phone_number(self) -> str:
        return self.phone

    class Config:
        from_attributes = True


class PatientDetailResponse(BaseModel):
    name: str
    gender: GenderEnum
    phone: str
    age: int

    @computed_field
    @property
    def phone_number(self) -> str:
        return self.phone

    class Config:
        from_attributes = True

