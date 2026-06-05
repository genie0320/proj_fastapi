"""
진료기록 관리 라우터
REQ-MDR-001 : 진료기록 등록
REQ-MDR-002 : 진료기록 목록 조회
REQ-MDR-003 : 진료기록 상세 조회
"""

import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from models.medical_record import MedicalRecord
from schemas.medical_record import (
    MedicalRecordDetail,
    MedicalRecordListItem,
    MedicalRecordListResponse,
)
from database import get_session

router = APIRouter(prefix="/medical-records", tags=["진료기록 관리"])

# X-Ray 이미지 로컬 저장 경로 (REQ-MDR-001 비고)
UPLOAD_DIR = Path("static/uploads/xray")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".dcm"}


# ── 유틸 ──────────────────────────────────────────────────────────────────────

def _validate_image(file: UploadFile) -> None:
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"지원하지 않는 파일 형식입니다. 허용: {ALLOWED_EXTENSIONS}",
        )


def _save_image(file: UploadFile) -> str:
    """이미지를 로컬에 저장하고 저장 경로 문자열을 반환한다."""
    ext = Path(file.filename).suffix.lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / filename
    with dest.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    return str(dest)


def _image_url(request: Request, path: str) -> str:
    """저장 경로 → 클라이언트 접근 URL 변환"""
    filename = Path(path).name
    return str(request.base_url) + f"static/uploads/xray/{filename}"


# ── REQ-MDR-001: 진료기록 등록 ────────────────────────────────────────────────

@router.post(
    "/",
    response_model=MedicalRecordDetail,
    status_code=status.HTTP_201_CREATED,
    summary="[REQ-MDR-001] 진료기록 등록",
)
async def create_medical_record(
    request: Request,
    patient_id:   int        = Form(..., description="환자 고유 ID"),
    chart_number: str        = Form(..., max_length=50, description="진료 차트 넘버"),
    symptoms:     str        = Form(..., description="진료된 증상"),
    xray_image:   UploadFile = File(..., description="흉부 X-Ray 이미지"),
    db: Session = Depends(get_session),
):
    _validate_image(xray_image)
    saved_path = _save_image(xray_image)

    record = MedicalRecord(
        patient_id=patient_id,
        chart_number=chart_number,
        symptoms=symptoms,
        xray_image_path=saved_path,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return MedicalRecordDetail(
        id=record.id,
        patient_id=record.patient_id,
        chart_number=record.chart_number,
        symptoms=record.symptoms,
        xray_image_url=_image_url(request, record.xray_image_path),
        created_at=record.created_at,
    )


# ── REQ-MDR-002: 진료기록 목록 조회 ───────────────────────────────────────────

@router.get(
    "/patient/{patient_id}",
    response_model=MedicalRecordListResponse,
    summary="[REQ-MDR-002] 환자별 진료기록 목록 조회",
)
def list_medical_records(
    patient_id: int,
    db: Session = Depends(get_session),
):
    records = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.created_at.desc())
        .all()
    )

    return MedicalRecordListResponse(
        total=len(records),
        records=[MedicalRecordListItem.from_record(r) for r in records],
    )


# ── REQ-MDR-003: 진료기록 상세 조회 ───────────────────────────────────────────

@router.get(
    "/{record_id}",
    response_model=MedicalRecordDetail,
    summary="[REQ-MDR-003] 진료기록 상세 조회",
)
def get_medical_record(
    record_id: int,
    request: Request,
    db: Session = Depends(get_session),
):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"진료기록 ID {record_id}을(를) 찾을 수 없습니다.",
        )

    return MedicalRecordDetail(
        id=record.id,
        patient_id=record.patient_id,
        chart_number=record.chart_number,
        symptoms=record.symptoms,
        xray_image_url=_image_url(request, record.xray_image_path),
        created_at=record.created_at,
    )