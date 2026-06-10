import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime
from app.core.db.databases import Base


class DepartmentEnum(str, enum.Enum):
    RESEARCH = "연구"
    MEDICAL = "의료"
    DEV = "개발"


class GenderEnum(str, enum.Enum):
    M = "M"
    F = "F"


class RoleEnum(str, enum.Enum):
    PENDING = "대기자"
    STAFF = "스태프"
    ADMIN = "어드민"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(50), nullable=False)
    department = Column(Enum(DepartmentEnum), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    phone = Column(String(20), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
