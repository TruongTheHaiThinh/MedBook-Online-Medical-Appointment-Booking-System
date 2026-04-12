from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.medicine import Medicine
from app.models.prescription import Prescription, PrescriptionItem
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.prescription import (
    PrescriptionCreate, PrescriptionResponse, MedicineResponse
)
from app.core.security import get_current_user, require_doctor

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])

@router.get("/medicines", response_model=List[MedicineResponse])
async def search_medicines(
    q: str = Query("", description="Search by name or indication"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Tìm kiếm thuốc từ dataset"""
    query = select(Medicine)
    if q:
        query = query.where(
            or_(
                Medicine.name.ilike(f"%{q}%"),
                Medicine.indication.ilike(f"%{q}%")
            )
        )
    result = await db.execute(query.limit(limit))
    return result.scalars().all()

@router.post("", response_model=PrescriptionResponse, status_code=201)
async def create_prescription(
    data: PrescriptionCreate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ tạo đơn thuốc cho một cuộc hẹn"""
    # Verify doctor
    dr_result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = dr_result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=403, detail="Chỉ bác sĩ mới được kê đơn")

    # Verify appointment
    appt_result = await db.execute(
        select(Appointment).where(
            Appointment.id == data.appointment_id,
            Appointment.doctor_id == doctor.id
        )
    )
    appointment = appt_result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc hẹn phù hợp")

    # Check if prescription already exists
    existing = await db.execute(select(Prescription).where(Prescription.appointment_id == data.appointment_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Cuộc hẹn này đã có đơn thuốc")

    prescription = Prescription(
        appointment_id=data.appointment_id,
        patient_id=appointment.patient_id,
        doctor_id=doctor.id,
        diagnosis=data.diagnosis,
        advice=data.advice,
        patient_age=data.patient_age,
        patient_weight=data.patient_weight,
        patient_height=data.patient_height,
        patient_address=data.patient_address
    )
    db.add(prescription)
    await db.flush() # Get prescription ID

    for item in data.items:
        p_item = PrescriptionItem(
            prescription_id=prescription.id,
            medicine_name=item.medicine_name,
            dosage=item.dosage,
            frequency=item.frequency,
            duration=item.duration,
            morning=item.morning,
            noon=item.noon,
            afternoon=item.afternoon,
            evening=item.evening,
            total_quantity=item.total_quantity,
            instructions=item.instructions
        )
        db.add(p_item)

    await db.commit()
    
    # Reload with items
    result = await db.execute(
        select(Prescription)
        .options(selectinload(Prescription.items))
        .where(Prescription.id == prescription.id)
    )
    return result.scalar_one()

@router.get("/appointment/{appointment_id}", response_model=PrescriptionResponse)
async def get_prescription(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Lấy đơn thuốc của một cuộc hẹn"""
    result = await db.execute(
        select(Prescription)
        .options(selectinload(Prescription.items))
        .where(Prescription.appointment_id == appointment_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn thuốc")
    return p

@router.put("/appointment/{appointment_id}", response_model=PrescriptionResponse)
async def update_prescription(
    appointment_id: UUID,
    data: PrescriptionCreate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Cập nhật đơn thuốc đã kê"""
    # Verify doctor
    dr_result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = dr_result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=403, detail="Chỉ bác sĩ mới được cập nhật đơn")

    # Get existing prescription
    res = await db.execute(
        select(Prescription)
        .options(selectinload(Prescription.items))
        .where(Prescription.appointment_id == appointment_id)
    )
    prescription = res.scalar_one_or_none()
    if not prescription:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn thuốc để cập nhật")

    # Check ownership
    if prescription.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền chỉnh sửa đơn của bác sĩ khác")

    # Update main fields
    prescription.diagnosis = data.diagnosis
    prescription.advice = data.advice
    prescription.patient_age = data.patient_age
    prescription.patient_weight = data.patient_weight
    prescription.patient_height = data.patient_height
    prescription.patient_address = data.patient_address

    # Replace items: Delete old ones, add new ones
    from app.models.prescription import PrescriptionItem
    from sqlalchemy import delete
    await db.execute(delete(PrescriptionItem).where(PrescriptionItem.prescription_id == prescription.id))

    for item in data.items:
        p_item = PrescriptionItem(
            prescription_id=prescription.id,
            medicine_name=item.medicine_name,
            dosage=item.dosage,
            frequency=item.frequency,
            duration=item.duration,
            morning=item.morning,
            noon=item.noon,
            afternoon=item.afternoon,
            evening=item.evening,
            total_quantity=item.total_quantity,
            instructions=item.instructions
        )
        db.add(p_item)

    await db.commit()
    await db.refresh(prescription)
    
    # Reload with items
    result = await db.execute(
        select(Prescription)
        .options(selectinload(Prescription.items))
        .where(Prescription.id == prescription.id)
    )
    return result.scalar_one()
