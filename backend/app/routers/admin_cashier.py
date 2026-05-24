"""
Cashier Admin Router – Xác nhận đặt lịch, QR check-in, đơn thuốc, thanh toán.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.appointment import Appointment, MedicalRecord, Payment
from app.models.doctor import Doctor
from app.models.specialty import Specialty
from app.schemas.appointment import (
    AppointmentResponse, MedicalRecordResponse, PaymentCreate, PaymentResponse,
)
from app.core.security import require_cashier_admin, RoleChecker
from app.services.appointment_service import AppointmentService
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/admin/cashier", tags=["Cashier Admin"])


async def _enrich_appointment(appt: Appointment, db: AsyncSession) -> AppointmentResponse:
    pt_res = await db.execute(select(User).where(User.id == appt.patient_id))
    patient = pt_res.scalar_one_or_none()
    dr_res = await db.execute(
        select(User.full_name, Specialty.name.label("spec"), Doctor.room_number)
        .join(Doctor, Doctor.user_id == User.id)
        .outerjoin(Specialty, Specialty.id == Doctor.specialty_id)
        .where(Doctor.id == appt.doctor_id)
    )
    dr_data = dr_res.first()
    
    # Fetch Payment
    p_res = await db.execute(select(Payment).where(Payment.appointment_id == appt.id))
    payment = p_res.scalar_one_or_none()
    
    return AppointmentResponse(
        id=appt.id,
        patient_id=appt.patient_id,
        doctor_id=appt.doctor_id,
        scheduled_date=appt.scheduled_date,
        scheduled_time=appt.scheduled_time,
        reason=appt.reason,
        status=appt.status,
        is_revisit=appt.is_revisit,
        qr_code=appt.qr_code,
        doctor_notes=appt.doctor_notes,
        reminder_sent=appt.reminder_sent,
        created_at=appt.created_at,
        patient_name=patient.full_name if patient else None,
        patient_phone=patient.phone if patient else None,
        patient_code=patient.patient_code if patient else "MB-XXX",
        doctor_name=dr_data[0] if dr_data else None,
        specialty_name=dr_data[1] if dr_data else None,
        queue_number=appt.queue_number,
        room_number=appt.room_number or (dr_data[2] if dr_data else "---"),
        payment_amount=float(payment.amount) if payment else 0,
        payment_status=payment.status if payment else "PENDING"
    )


# ── Pending appointments (dashboard) ──

@router.get("/appointments/pending", response_model=List[AppointmentResponse])
async def list_pending(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_cashier_admin),
    db: AsyncSession = Depends(get_db),
):
    """Danh sách lịch hẹn chờ xác nhận"""
    result = await db.execute(
        select(Appointment)
        .where(Appointment.status == "PENDING")
        .order_by(Appointment.created_at.asc())
        .offset((page - 1) * size).limit(size)
    )
    appointments = result.scalars().all()
    return [await _enrich_appointment(a, db) for a in appointments]


@router.get("/appointments/confirmed", response_model=List[AppointmentResponse])
async def list_confirmed(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_cashier_admin),
    db: AsyncSession = Depends(get_db),
):
    """Danh sách lịch hẹn đã xác nhận (chờ bệnh nhân đến)"""
    result = await db.execute(
        select(Appointment)
        .where(Appointment.status == "CONFIRMED")
        .order_by(Appointment.scheduled_date.asc())
        .offset((page - 1) * size).limit(size)
    )
    appointments = result.scalars().all()
    return [await _enrich_appointment(a, db) for a in appointments]


# ── Prescriptions waiting for payment ──

@router.get("/prescriptions/pending", response_model=List[AppointmentResponse])
async def list_prescriptions_pending(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_cashier_admin),
    db: AsyncSession = Depends(get_db),
):
    """Lịch hẹn có đơn thuốc chờ thu phí"""
    result = await db.execute(
        select(Appointment)
        .where(Appointment.status == "PRESCRIPTION_SENT")
        .order_by(Appointment.created_at.asc())
        .offset((page - 1) * size).limit(size)
    )
    appointments = result.scalars().all()
    return [await _enrich_appointment(a, db) for a in appointments]


@router.get("/prescriptions/{appointment_id}", response_model=MedicalRecordResponse)
async def get_prescription_detail(
    appointment_id: UUID,
    current_user: User = Depends(require_cashier_admin),
    db: AsyncSession = Depends(get_db),
):
    """Xem chi tiết đơn thuốc của một lịch hẹn"""
    result = await db.execute(
        select(MedicalRecord)
        .options(selectinload(MedicalRecord.prescriptions))
        .where(MedicalRecord.appointment_id == appointment_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ khám bệnh")
    return record


# ── Payment ──

@router.post("/payments", response_model=PaymentResponse, status_code=201)
async def create_payment(
    data: PaymentCreate,
    current_user: User = Depends(require_cashier_admin),
    db: AsyncSession = Depends(get_db),
):
    """Thu phí đơn thuốc → PRESCRIPTION_SENT → COMPLETED"""
    return await PaymentService.create_payment(
        appointment_id=data.appointment_id,
        amount=data.amount,
        payment_method=data.payment_method,
        cashier=current_user,
        db=db,
    )


@router.get("/payments/{appointment_id}", response_model=PaymentResponse)
async def get_payment(
    appointment_id: UUID,
    current_user: User = Depends(require_cashier_admin),
    db: AsyncSession = Depends(get_db),
):
    """Xem thông tin thanh toán"""
    return await PaymentService.get_by_appointment(appointment_id, db)


# ── Revenue ──

@router.get("/revenue")
async def get_revenue(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_cashier_admin),
    db: AsyncSession = Depends(get_db),
):
    """Thống kê doanh thu"""
    return await PaymentService.get_revenue_summary(db, days)


# ── QR Check-in ──

@router.post("/checkin-qr", response_model=AppointmentResponse)
async def checkin_by_qr(
    qr_code: str = Query(..., description="Mã QR lịch hẹn"),
    current_user: User = Depends(require_cashier_admin),
    db: AsyncSession = Depends(get_db),
):
    """Quét QR check-in bệnh nhân: CONFIRMED → IN_PROGRESS"""
    appt = await AppointmentService.checkin_by_qr(qr_code, db, current_user)
    return await _enrich_appointment(appt, db)
