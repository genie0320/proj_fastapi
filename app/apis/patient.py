from uuid import UUID
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db.databases import async_get_db
from app.models.patient import Patient
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientDetailResponse,
)
from app.apis.user import get_current_user

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PatientResponse)
async def create_patient(
    patient_in: PatientCreate,
    db: AsyncSession = Depends(async_get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Register a new patient (REQ-PTNT-001).
    Restricted to users with 'Staff' or 'Admin' role.
    """
    if current_user.get("role") not in ["Staff", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    patient = Patient(**patient_in.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.get("/", response_model=list[PatientResponse])
async def list_patients(
    name: str | None = Query(None, description="Filter by name (substring search)"),
    gender: str | None = Query(None, description="Filter by exact gender"),
    min_age: int | None = Query(None, description="Minimum age filter"),
    max_age: int | None = Query(None, description="Maximum age filter"),
    db: AsyncSession = Depends(async_get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    List all patients with optional filtering parameters (REQ-PTNT-002).
    Requires a valid authenticated user.
    """
    stmt = select(Patient)
    
    if name:
        stmt = stmt.where(Patient.name.contains(name))
    if gender:
        stmt = stmt.where(Patient.gender == gender)
    if min_age is not None:
        stmt = stmt.where(Patient.age >= min_age)
    if max_age is not None:
        stmt = stmt.where(Patient.age <= max_age)
        
    result = await db.execute(stmt)
    patients = result.scalars().all()
    return patients


@router.get("/{patient_id}", response_model=PatientDetailResponse)
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(async_get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Fetch single patient details (REQ-PTNT-003).
    Includes mocked medical records to unblock frontend / other teams.
    Requires a valid authenticated user.
    """
    stmt = select(Patient).where(Patient.uuid == patient_id)
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
        
    # Inject mock medical records as required for coordination interlocking (REQ-PTNT-003 Contract)
    mock_records = [
        {
            "record_id": "rec-001",
            "diagnosis": "Essential hypertension",
            "treatment": "Prescribed Lisinopril 10mg daily",
            "recorded_at": "2026-05-10T09:30:00Z"
        },
        {
            "record_id": "rec-002",
            "diagnosis": "Type 2 diabetes mellitus",
            "treatment": "Metformin 500mg twice daily, diet counseling",
            "recorded_at": "2026-06-01T14:15:00Z"
        }
    ]
    
    # Construct response cleanly in one shot without post-validation mutation
    patient_data = PatientResponse.model_validate(patient).model_dump()
    return PatientDetailResponse(**patient_data, medical_records=mock_records)


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: UUID,
    patient_in: PatientUpdate,
    db: AsyncSession = Depends(async_get_db),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Update a patient's name or contact number (REQ-PTNT-004).
    Restricted to users with 'Staff' or 'Admin' role.
    """
    if current_user.get("role") not in ["Staff", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    stmt = select(Patient).where(Patient.uuid == patient_id)
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
        
    update_data = patient_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)
        
    await db.commit()
    await db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(async_get_db),
    current_user: dict = Depends(get_current_user)
) -> None:
    """
    Hard delete a patient from the database (REQ-PTNT-005).
    Restricted to users with 'Staff' or 'Admin' role.
    """
    if current_user.get("role") not in ["Staff", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    stmt = select(Patient).where(Patient.uuid == patient_id)
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
        
    await db.delete(patient)
    await db.commit()
