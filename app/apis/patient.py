# app/apis/patient.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db  # AG가 확인한 비동기 주입기 명칭 적용
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientListResponse,
    PatientDetailResponse,
)
from app.services.patient_service import PatientService

router = APIRouter(prefix="/api/v1/patients", tags=["Patient Management"])


@router.post(
    "", response_model=PatientDetailResponse, status_code=status.HTTP_201_CREATED
)
async def create_patient(
    payload: PatientCreate, db: AsyncSession = Depends(async_get_db)
):
    return await PatientService.create_patient(db=db, payload=payload)


@router.get(
    "", response_model=List[PatientListResponse], status_code=status.HTTP_200_OK
)
async def get_patients(
    name: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    min_age: Optional[int] = Query(None),
    max_age: Optional[int] = Query(None),
    db: AsyncSession = Depends(async_get_db),
):
    return await PatientService.get_filtered_patients(
        db=db, name=name, gender=gender, min_age=min_age, max_age=max_age
    )


@router.get(
    "/{patient_id}",
    response_model=PatientDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def get_patient_detail(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    patient = await PatientService.get_patient_by_id(db=db, patient_id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    return patient


@router.patch(
    "/{patient_id}",
    response_model=PatientDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def update_patient(
    patient_id: int, payload: PatientUpdate, db: AsyncSession = Depends(async_get_db)
):
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    patient = await PatientService.update_patient(
        db=db, patient_id=patient_id, payload=payload
    )
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(async_get_db),
):
    image_paths = await PatientService.prepare_delete_patient(
        db=db, patient_id=patient_id
    )
    if image_paths is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )

    if image_paths:
        background_tasks.add_task(
            PatientService.execute_cascade_file_deletion, image_paths
        )

    return


from sqlalchemy import select
from app.models.record import MedicalRecord

@router.get("/{patient_id}/medical-records", status_code=status.HTTP_200_OK)
async def get_patient_medical_records(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.patient_id == patient_id))
    records = result.scalars().all()
    return records

