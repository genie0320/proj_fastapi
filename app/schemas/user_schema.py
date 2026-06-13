import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator, computed_field

from app.core.security import validate_password_rule
from app.models.user import DepartmentEnum, GenderEnum, RoleEnum


def validate_email_format(email: str) -> str:
    if len(email) > 100:
        raise ValueError("이메일은 최대 100자까지 입력 가능합니다.")
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValueError("올바른 이메일 형식이 아닙니다.")
    return email


def validate_phone_format(phone: str) -> str:
    digits = re.sub(r"[^\d]", "", phone)
    if len(digits) == 11 and digits.startswith("010"):
        phone = f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    pattern = r"^010-\d{4}-\d{4}$"
    if not re.match(pattern, phone):
        raise ValueError("휴대폰 번호는 010-0000-0000 형식이어야 합니다.")
    return phone


class UserSignupRequest(BaseModel):
    email: str
    password: str
    name: str
    department: DepartmentEnum
    gender: GenderEnum
    phone: str

    @model_validator(mode="before")
    @classmethod
    def populate_fields(cls, data: any) -> any:
        if isinstance(data, dict):
            if "phone_number" in data and "phone" not in data:
                data["phone"] = data["phone_number"]
            if "department" in data:
                dept = data["department"]
                if dept in ["developer", "개발팀"]:
                    data["department"] = DepartmentEnum.DEV
                elif dept in ["medical team", "의료진"]:
                    data["department"] = DepartmentEnum.MEDICAL
                elif dept in ["researcher", "연구진"]:
                    data["department"] = DepartmentEnum.RESEARCH
            if "gender" in data:
                gen = data["gender"]
                if gen in ["male", "남성"]:
                    data["gender"] = GenderEnum.M
                elif gen in ["female", "여성"]:
                    data["gender"] = GenderEnum.F
        return data

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return validate_email_format(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_rule(value)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not (2 <= len(value) <= 50):
            raise ValueError("이름은 2자 이상 50자 이하여야 합니다.")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return validate_phone_format(value)


class UserLoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return validate_email_format(value)


class UserUpdateRequest(BaseModel):
    department: DepartmentEnum | None = None
    phone: str | None = None

    @model_validator(mode="before")
    @classmethod
    def populate_fields(cls, data: any) -> any:
        if isinstance(data, dict):
            if "phone_number" in data and "phone" not in data:
                data["phone"] = data["phone_number"]
            if "department" in data:
                dept = data["department"]
                if dept in ["developer", "개발팀"]:
                    data["department"] = DepartmentEnum.DEV
                elif dept in ["medical team", "의료진"]:
                    data["department"] = DepartmentEnum.MEDICAL
                elif dept in ["researcher", "연구진"]:
                    data["department"] = DepartmentEnum.RESEARCH
        return data

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_phone_format(value)


class UserPasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return validate_password_rule(value)


class UserRoleUpdateRequest(BaseModel):
    role: RoleEnum


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    department: DepartmentEnum
    gender: GenderEnum
    phone: str
    role: RoleEnum
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def phone_number(self) -> str:
        return self.phone


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    message: str

