from typing import List
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreate, AppointmentConfirm, AppointmentCancel, AppointmentResponse, AppointmentComplete
)
from app.core.security import get_current_user, require_patient, require_doctor
from app.core.email import send_appointment_email

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def _build_response(appointment: Appointment, patient_name: str = None, doctor_name: str = None, specialty_name: str = None) -> AppointmentResponse:
    return AppointmentResponse(
        id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        scheduled_date=appointment.scheduled_date,
        scheduled_time=appointment.scheduled_time,
        reason=appointment.reason,
        status=appointment.status,
        doctor_notes=appointment.doctor_notes,
        reminder_sent=appointment.reminder_sent,
        created_at=appointment.created_at,
        patient_name=patient_name,
        doctor_name=doctor_name,
        specialty_name=specialty_name,
    )


@router.post("", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(require_patient),
    db: AsyncSession = Depends(get_db)
):
    """Bệnh nhân đặt lịch hẹn"""
    from datetime import date as date_type

    if data.scheduled_date < datetime.now().date():
        raise HTTPException(status_code=400, detail="Không thể đặt lịch trong quá khứ")

    # Check doctor exists and is approved
    result = await db.execute(
        select(Doctor, User)
        .join(User, Doctor.user_id == User.id)
        .where(Doctor.id == data.doctor_id, Doctor.is_approved == True)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Bác sĩ không tồn tại hoặc chưa được phê duyệt")
    doctor, doctor_user = row

    # Check patient doesn't already have an appointment at the same time
    result = await db.execute(
        select(Appointment).where(
            Appointment.patient_id == current_user.id,
            Appointment.scheduled_date == data.scheduled_date,
            Appointment.scheduled_time == data.scheduled_time,
            Appointment.status.in_(["PENDING", "CONFIRMED"])
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Bạn đã có lịch hẹn khác vào cùng giờ này")

    # Check slot availability with SELECT FOR UPDATE (race condition protection)
    async with db.begin_nested():
        result = await db.execute(
            select(Appointment).where(
                Appointment.doctor_id == data.doctor_id,
                Appointment.scheduled_date == data.scheduled_date,
                Appointment.scheduled_time == data.scheduled_time,
                Appointment.status.in_(["PENDING", "CONFIRMED"])
            ).with_for_update()
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Slot này đã được đặt, vui lòng chọn giờ khác")

        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=data.doctor_id,
            scheduled_date=data.scheduled_date,
            scheduled_time=data.scheduled_time,
            reason=data.reason,
            status="PENDING",
        )
        db.add(appointment)

    await db.commit()
    await db.refresh(appointment)

    # Send confirmation email asynchronously (fire-and-forget)
    import asyncio
    asyncio.create_task(
        send_appointment_email(
            to_email=current_user.email,
            title="Đặt lịch hẹn thành công",
            message="Lịch hẹn của bạn đã được đặt thành công và đang chờ bác sĩ xác nhận.",
            patient_name=current_user.full_name,
            doctor_name=doctor_user.full_name,
            scheduled_date=str(data.scheduled_date),
            scheduled_time=str(data.scheduled_time),
            reason=data.reason,
        )
    )

    return _build_response(appointment, current_user.full_name, doctor_user.full_name)


@router.get("/me", response_model=List[AppointmentResponse])
async def get_my_appointments(
    status: str = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bệnh nhân xem danh sách lịch hẹn của mình"""
    query = select(Appointment).where(Appointment.patient_id == current_user.id)
    if status:
        query = query.where(Appointment.status == status.upper())
    query = query.order_by(Appointment.scheduled_date.desc()).offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    appointments = result.scalars().all()

    responses = []
    for appt in appointments:
        # Get doctor name and specialty
        dr_query = (
            select(User.full_name, Specialty.name.label("specialty_name"))
            .join(Doctor, Doctor.user_id == User.id)
            .join(Specialty, Specialty.id == Doctor.specialty_id)
            .where(Doctor.id == appt.doctor_id)
        )
        dr_res = await db.execute(dr_query)
        dr_data = dr_res.first()
        
        dr_name = dr_data[0] if dr_data else "Bác sĩ"
        sp_name = dr_data[1] if dr_data else "---"
        
        responses.append(_build_response(appt, current_user.full_name, dr_name, sp_name))

    return responses


@router.get("/doctor/list", response_model=List[AppointmentResponse])
async def get_doctor_appointments(
    status: str = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ xem danh sách lịch hẹn của mình"""
    result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bác sĩ")

    query = select(Appointment).where(Appointment.doctor_id == doctor.id)
    if status:
        query = query.where(Appointment.status == status.upper())
    query = query.order_by(Appointment.scheduled_date.asc()).offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    appointments = result.scalars().all()

    # Fetch specialty name for the doctor
    from app.models.prescription import Prescription, PrescriptionItem
    from app.models.specialty import Specialty
    spec_result = await db.execute(select(Specialty).where(Specialty.id == doctor.specialty_id))
    specialty = spec_result.scalar_one_or_none()
    spec_name = specialty.name if specialty else None

    responses = []
    for appt in appointments:
        pt_result = await db.execute(select(User).where(User.id == appt.patient_id))
        patient_user = pt_result.scalar_one_or_none()
        responses.append(_build_response(appt, patient_user.full_name if patient_user else None, current_user.full_name, spec_name))
    return responses


@router.patch("/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(
    appointment_id: UUID,
    data: AppointmentConfirm,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ xác nhận lịch hẹn PENDING → CONFIRMED"""
    result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bác sĩ")

    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id, Appointment.doctor_id == doctor.id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")

    if appointment.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Không thể xác nhận lịch hẹn đang ở trạng thái {appointment.status}")

    appointment.status = "CONFIRMED"
    if data.doctor_notes:
        appointment.doctor_notes = data.doctor_notes
    await db.commit()
    await db.refresh(appointment)

    # Get patient info for email
    pt_result = await db.execute(select(User).where(User.id == appointment.patient_id))
    patient = pt_result.scalar_one_or_none()
    if patient:
        import asyncio
        asyncio.create_task(
            send_appointment_email(
                to_email=patient.email,
                title="Lịch hẹn đã được xác nhận",
                message="Bác sĩ đã xác nhận lịch hẹn của bạn.",
                patient_name=patient.full_name,
                doctor_name=current_user.full_name,
                scheduled_date=str(appointment.scheduled_date),
                scheduled_time=str(appointment.scheduled_time),
                doctor_notes=appointment.doctor_notes,
            )
        )

    return _build_response(appointment, patient.full_name if patient else None, current_user.full_name)


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: UUID,
    data: AppointmentCancel,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Hủy lịch hẹn (bệnh nhân chỉ được hủy trước 24h, bác sĩ/admin không giới hạn)"""
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")

    # Authorization check
    if current_user.role == "patient":
        if appointment.patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Không có quyền hủy lịch này")
        # 24-hour restriction
        scheduled_dt = datetime.combine(appointment.scheduled_date, appointment.scheduled_time)
        if datetime.now() > scheduled_dt - timedelta(hours=24):
            raise HTTPException(status_code=400, detail="Chỉ được hủy lịch trước 24 giờ so với giờ khám")
    elif current_user.role == "doctor":
        dr_result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
        doctor = dr_result.scalar_one_or_none()
        if not doctor or appointment.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Không có quyền hủy lịch này")

    if appointment.status not in ["PENDING", "CONFIRMED"]:
        raise HTTPException(status_code=400, detail=f"Không thể hủy lịch đang ở trạng thái {appointment.status}")

    appointment.status = "CANCELLED"
    appointment.doctor_notes = data.doctor_notes
    await db.commit()
    await db.refresh(appointment)

    # Notify patient
    pt_result = await db.execute(select(User).where(User.id == appointment.patient_id))
    patient = pt_result.scalar_one_or_none()
    dr_user_result = await db.execute(
        select(User).join(Doctor, Doctor.user_id == User.id).where(Doctor.id == appointment.doctor_id)
    )
    doctor_user = dr_user_result.scalar_one_or_none()

    if patient and patient.id != current_user.id:
        import asyncio
        asyncio.create_task(
            send_appointment_email(
                to_email=patient.email,
                title="Lịch hẹn đã bị hủy",
                message="Lịch hẹn của bạn đã bị hủy.",
                patient_name=patient.full_name,
                doctor_name=doctor_user.full_name if doctor_user else "Bác sĩ",
                scheduled_date=str(appointment.scheduled_date),
                scheduled_time=str(appointment.scheduled_time),
                doctor_notes=data.doctor_notes,
            )
        )

    return _build_response(
        appointment,
        patient.full_name if patient else None,
        doctor_user.full_name if doctor_user else None
    )


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
async def complete_appointment(
    appointment_id: UUID,
    data: AppointmentComplete,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ đánh dấu ca khám hoàn thành CONFIRMED → COMPLETED"""
    result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bác sĩ")

    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id, Appointment.doctor_id == doctor.id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")

    if appointment.status != "CONFIRMED":
        raise HTTPException(status_code=400, detail="Chỉ có thể hoàn thành lịch hẹn đã CONFIRMED")

    appointment.status = "COMPLETED"
    if data.doctor_notes:
        appointment.doctor_notes = data.doctor_notes
    await db.commit()
    await db.refresh(appointment)

    pt_result = await db.execute(select(User).where(User.id == appointment.patient_id))
    patient = pt_result.scalar_one_or_none()

    return _build_response(appointment, patient.full_name if patient else None, current_user.full_name)
