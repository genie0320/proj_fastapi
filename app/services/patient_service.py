# app/services/patient_service.py
import os
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate

from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)


class PatientService:

    @staticmethod
    async def create_patient(db: AsyncSession, payload: PatientCreate) -> Patient:
        # REQ-PTNT-001: 환자 정보 등록
        new_patient = Patient(
            name=payload.name,
            age=payload.age,
            gender=payload.gender,
            phone=payload.phone,
        )
        db.add(new_patient)
        await db.commit()
        await db.refresh(new_patient)
        return new_patient

    @staticmethod
    async def get_filtered_patients(
        db: AsyncSession,
        name: Optional[str] = None,
        gender: Optional[str] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
    ) -> List[Patient]:
        # REQ-PTNT-002: 이름 검색 및 성별, 나이 범위 필터링 목록 조회
        query = select(Patient)
        filters = []

        if name:
            filters.append(Patient.name.contains(name))
        if gender:
            filters.append(Patient.gender == gender)
        if min_age is not None:
            filters.append(Patient.age >= min_age)
        if max_age is not None:
            filters.append(Patient.age <= max_age)

        if filters:
            query = query.where(and_(*filters))

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_patient_by_id(db: AsyncSession, patient_id: int) -> Optional[Patient]:
        # REQ-PTNT-003: 환자 상세 조회
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_patient(
        db: AsyncSession, patient_id: int, payload: PatientUpdate
    ) -> Optional[Patient]:
        # REQ-PTNT-004: 환자 정보 수정 (이름, 연락처만 제한적 수정 가능)
        patient = await PatientService.get_patient_by_id(db, patient_id)
        if not patient:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(patient, key, value)

        await db.commit()
        await db.refresh(patient)
        return patient

    @staticmethod
    async def prepare_delete_patient(
        db: AsyncSession, patient_id: int
    ) -> Optional[List[str]]:
        """
        REQ-PTNT-005: 삭제 전 대상 존재 확인 및 로컬 파일 경로 추출 후 DB 레코드 삭제
        """
        # 관계형 쿼리로 진료기록(MedicalRecord)에 연동된 이미지 경로 선추출 필요 (selectinload 적용하여 MissingGreenlet 방지)
        result = await db.execute(
            select(Patient)
            .options(selectinload(Patient.medical_records))
            .where(Patient.id == patient_id)
        )
        patient = result.scalar_one_or_none()
        if not patient:
            return None

        image_paths = []
        # 다른 조원이 구성할 medical_records 구조가 있다고 가정할 때의 방어적 추출
        if hasattr(patient, "medical_records") and patient.medical_records:
            for record in patient.medical_records:
                if hasattr(record, "image_path") and record.image_path:
                    image_paths.append(record.image_path)

        # DB 레코드 삭제 (Cascade 설정에 의해 medical_records도 같이 날아감)
        await db.delete(patient)
        await db.commit()
        return image_paths

    @staticmethod
    def execute_cascade_file_deletion(image_paths: List[str]):
        """NFR-PTNT-001 성능 만족을 위해 백그라운드에서 동기 디스크 I/O를 비동기식으로 처리"""
        for path in image_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    logger.info(f"Successfully deleted X-Ray file: {path}")
            except Exception as e:
                logger.error(f"Failed to delete file {path}: {str(e)}")
