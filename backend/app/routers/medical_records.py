"""
Medical Records Router – Hồ sơ khám bệnh, kê đơn thuốc, sổ khám điện tử.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database import get_db
from app.models.user import User
from app.models.medicine import Medicine
from app.models.appointment import MedicalRecord
from app.schemas.appointment import MedicalRecordCreate, MedicalRecordResponse
from app.schemas.prescription import MedicineResponse
from app.core.security import get_current_user, require_doctor, require_patient, RoleChecker
from app.services.medical_service import MedicalService

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])


# ── Doctor: create / update medical record ──

@router.post("", response_model=MedicalRecordResponse, status_code=201)
async def create_medical_record(
    data: MedicalRecordCreate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Bác sĩ tạo hồ sơ khám + kê đơn thuốc → chuyển trạng thái PRESCRIPTION_SENT"""
    return await MedicalService.create_record(data, current_user, db)


@router.put("/{appointment_id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    appointment_id: UUID,
    data: MedicalRecordCreate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Bác sĩ cập nhật hồ sơ khám"""
    return await MedicalService.update_record(appointment_id, data, current_user, db)


# ── View medical record ──

@router.get("/appointment/{appointment_id}", response_model=MedicalRecordResponse)
async def get_record_by_appointment(
    appointment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Xem hồ sơ khám theo lịch hẹn"""
    return await MedicalService.get_by_appointment(appointment_id, db)


# ── Patient: Sổ khám bệnh điện tử (read-only) ──

@router.get("/my-history", response_model=List[MedicalRecordResponse])
async def get_my_history(
    current_user: User = Depends(require_patient),
    db: AsyncSession = Depends(get_db),
):
    """Bệnh nhân xem toàn bộ lịch sử khám bệnh"""
    return await MedicalService.get_patient_history(current_user.id, db)


# ── Doctor: search patient history ──

@router.get("/patient/{patient_id}", response_model=List[MedicalRecordResponse])
async def get_patient_history(
    patient_id: UUID,
    current_user: User = Depends(RoleChecker(["doctor", "hr_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Bác sĩ và Admin hệ thống tra cứu hồ sơ bệnh nhân"""
    return await MedicalService.get_patient_history(patient_id, db)


# ── Medicine search (for prescription form) ──

@router.get("/medicines", response_model=List[MedicineResponse])
async def search_medicines(
    q: str = Query("", description="Tìm theo tên hoặc chỉ định"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Tìm kiếm thuốc từ dataset"""
    query = select(Medicine)
    if q:
        query = query.where(
            or_(Medicine.name.ilike(f"%{q}%"), Medicine.indication.ilike(f"%{q}%"))
        )
    result = await db.execute(query.limit(limit))
    return result.scalars().all()
