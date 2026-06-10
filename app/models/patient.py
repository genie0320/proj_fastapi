import enum
from sqlalchemy import String, SmallInteger, BigInteger, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.databases import Base
from app.core.db.models import UUIDMixin, TimestampMixin


class GenderEnum(str, enum.Enum):
    """ERD의 gender 'E'(Enum) 명세를 충족하기 위한 파이썬 열거형 클래스"""

    MALE = "MALE"
    FEMALE = "FEMALE"


class Patient(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "patients"

    __table_args__ = (
        UniqueConstraint("uuid", name="uq_patients_uuid"),
    )

    # 1. ERD 기준: id bigint PK
    # (UUIDMixin이 존재하더라도 ERD상 물리 PK인 id를 BigInteger로 명시적 선언)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # 2. ERD 기준: name varchar(30) NN
    name: Mapped[str] = mapped_column(String(30), nullable=False)

    # 3. ERD 기준: age smallint NN (기존 Integer에서 SmallInteger로 최적화)
    age: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # 4. ERD 기준: phone varchar(11) NN (phone_number에서 명칭 수정 및 길이 단축)
    phone: Mapped[str] = mapped_column(String(11), nullable=False)

    # 5. ERD 기준: gender gender E (단순 문자열이 아닌 데이터 무결성을 위한 Enum 매핑)
    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum), nullable=False)

    # 6. 상용 규격: 진료기록(MedicalRecord) 모델과의 연관 관계 및 종속 삭제 설정 (REQ-PTNT-005)
    medical_records: Mapped[list["MedicalRecord"]] = relationship(
        "MedicalRecord", back_populates="patient", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Patient(id={self.id}, name='{self.name}', phone='{self.phone}')>"
