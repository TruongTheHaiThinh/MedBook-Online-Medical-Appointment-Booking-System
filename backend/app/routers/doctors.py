from typing import List, Optional
from uuid import UUID
from datetime import date, time, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.doctor import Doctor
from app.models.specialty import Specialty
from app.models.schedule import Schedule
from app.models.appointment import Appointment
from app.models.leave_request import LeaveRequest
from app.models.user import User
from app.models.prescription import Prescription
from app.schemas.doctor import (
    DoctorProfileResponse, DoctorProfileUpdate, SpecialtyResponse,
    LeaveRequestCreate, LeaveRequestResponse
)
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, AvailableSlotsResponse
from app.core.security import get_current_user, require_doctor

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("", response_model=List[DoctorProfileResponse])
async def list_doctors(
    specialty_id: Optional[UUID] = None,
    name: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Danh sách bác sĩ (public) – lọc theo chuyên khoa hoặc tên"""
    query = (
        select(Doctor, User, Specialty)
        .join(User, Doctor.user_id == User.id)
        .outerjoin(Specialty, Doctor.specialty_id == Specialty.id)
        .where(Doctor.is_approved == True, User.is_active == True)
    )
    if specialty_id:
        query = query.where(Doctor.specialty_id == specialty_id)
    if name:
        query = query.where(User.full_name.ilike(f"%{name}%"))

    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    rows = result.all()

    doctors = []
    for doctor, user, specialty in rows:
        doctors.append(DoctorProfileResponse(
            id=doctor.id,
            user_id=doctor.user_id,
            specialty_id=doctor.specialty_id,
            bio=doctor.bio,
            experience_years=doctor.experience_years,
            is_approved=doctor.is_approved,
            full_name=user.full_name,
            email=user.email,
            specialty_name=specialty.name if specialty else None,
        ))
    return doctors


@router.get("/me", response_model=DoctorProfileResponse)
async def get_my_doctor_profile(
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ xem hồ sơ của mình"""
    result = await db.execute(
        select(Doctor, Specialty)
        .outerjoin(Specialty, Doctor.specialty_id == Specialty.id)
        .where(Doctor.user_id == current_user.id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bác sĩ")
    doctor, specialty = row
    return DoctorProfileResponse(
        id=doctor.id,
        user_id=doctor.user_id,
        specialty_id=doctor.specialty_id,
        bio=doctor.bio,
        experience_years=doctor.experience_years,
        is_approved=doctor.is_approved,
        full_name=current_user.full_name,
        email=current_user.email,
        specialty_name=specialty.name if specialty else None,
    )


@router.patch("/me", response_model=DoctorProfileResponse)
async def update_my_doctor_profile(
    data: DoctorProfileUpdate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ cập nhật hồ sơ cá nhân"""
    result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bác sĩ")

    if not doctor.is_approved:
        raise HTTPException(status_code=403, detail="Tài khoản bác sĩ chưa được phê duyệt")

    if data.bio is not None:
        doctor.bio = data.bio
    if data.experience_years is not None:
        doctor.experience_years = data.experience_years
    if data.specialty_id is not None:
        # Verify specialty exists
        spec_result = await db.execute(select(Specialty).where(Specialty.id == data.specialty_id))
        if not spec_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Chuyên khoa không tồn tại")
        doctor.specialty_id = data.specialty_id

    await db.commit()
    await db.refresh(doctor)

    spec_result = await db.execute(select(Specialty).where(Specialty.id == doctor.specialty_id))
    specialty = spec_result.scalar_one_or_none()

    return DoctorProfileResponse(
        id=doctor.id,
        user_id=doctor.user_id,
        specialty_id=doctor.specialty_id,
        bio=doctor.bio,
        experience_years=doctor.experience_years,
        is_approved=doctor.is_approved,
        full_name=current_user.full_name,
        email=current_user.email,
        specialty_name=specialty.name if specialty else None,
    )


@router.get("/{doctor_id}", response_model=DoctorProfileResponse)
async def get_doctor(doctor_id: UUID, db: AsyncSession = Depends(get_db)):
    """Xem thông tin 1 bác sĩ (public)"""
    result = await db.execute(
        select(Doctor, User, Specialty)
        .join(User, Doctor.user_id == User.id)
        .outerjoin(Specialty, Doctor.specialty_id == Specialty.id)
        .where(Doctor.id == doctor_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy bác sĩ")
    doctor, user, specialty = row
    return DoctorProfileResponse(
        id=doctor.id,
        user_id=doctor.user_id,
        specialty_id=doctor.specialty_id,
        bio=doctor.bio,
        experience_years=doctor.experience_years,
        is_approved=doctor.is_approved,
        full_name=user.full_name,
        email=user.email,
        specialty_name=specialty.name if specialty else None,
    )


# ── Schedule endpoints ──────────────────────────────────────────────────────

@router.post("/me/schedules", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    data: ScheduleCreate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ tạo lịch làm việc theo pattern tuần"""
    result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = result.scalar_one_or_none()
    if not doctor or not doctor.is_approved:
        raise HTTPException(status_code=403, detail="Tài khoản chưa được phê duyệt")

    schedule = Schedule(
        doctor_id=doctor.id,
        day_of_week=data.day_of_week,
        specific_date=data.specific_date,
        start_time=data.start_time,
        end_time=data.end_time,
        slot_duration_min=data.slot_duration_min,
        max_slots=data.max_slots,
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule


@router.get("/me/schedules", response_model=List[ScheduleResponse])
async def get_my_schedules(
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ xem lịch làm việc của mình"""
    result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bác sĩ")

    result = await db.execute(select(Schedule).where(Schedule.doctor_id == doctor.id))
    return result.scalars().all()


@router.delete("/me/schedules/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: UUID,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ xóa lịch làm việc"""
    result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bác sĩ")

    result = await db.execute(
        select(Schedule).where(
            Schedule.id == schedule_id,
            Schedule.doctor_id == doctor.id
        )
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch làm việc")

    await db.delete(schedule)
    await db.commit()
    return None


@router.get("/{doctor_id}/available-slots", response_model=AvailableSlotsResponse)
async def get_available_slots(
    doctor_id: UUID,
    date: date = Query(..., description="Ngày muốn đặt (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách slot trống của bác sĩ theo ngày (Smart Scheduling Engine)"""
    if date < datetime.now().date():
        raise HTTPException(status_code=400, detail="Không thể xem slot trong quá khứ")

    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id, Doctor.is_approved == True))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Bác sĩ không tồn tại hoặc chưa được phê duyệt")

    # Check if doctor is on leave
    lr_result = await db.execute(
        select(LeaveRequest).where(
            LeaveRequest.doctor_id == doctor_id,
            LeaveRequest.leave_date == date,
            LeaveRequest.status == "APPROVED"
        )
    )
    if lr_result.scalar_one_or_none():
        return AvailableSlotsResponse(doctor_id=doctor_id, date=str(date), slots=[])

    # day_of_week: Python's weekday(): 0=Monday,...,6=Sunday
    # Our DB: 0=Sunday, 1=Monday,...,6=Saturday
    python_weekday = date.weekday()  # 0=Mon, ..., 6=Sun
    db_day_of_week = (python_weekday + 1) % 7  # Convert: Mon=1,...,Sun=0

    from sqlalchemy import or_
    result = await db.execute(
        select(Schedule).where(
            Schedule.doctor_id == doctor_id,
            or_(
                Schedule.specific_date == date,
                and_(Schedule.day_of_week == db_day_of_week, Schedule.specific_date == None)
            )
        )
    )
    schedules = result.scalars().all()

    if not schedules:
        return AvailableSlotsResponse(doctor_id=doctor_id, date=str(date), slots=[])

    # Get all booked slots on that day
    result = await db.execute(
        select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.scheduled_date == date,
            Appointment.status.in_(["PENDING", "CONFIRMED"])
        )
    )
    booked = result.scalars().all()
    booked_times = {a.scheduled_time.strftime("%H:%M") for a in booked}

    # Generate available slots
    available_slots = []
    for schedule in schedules:
        current = datetime.combine(date, schedule.start_time)
        end = datetime.combine(date, schedule.end_time)
        slot_count = 0

        while current < end and slot_count < schedule.max_slots:
            # Only add slot if it's in the future (relevant if date is today)
            if current > datetime.now():
                slot_str = current.strftime("%H:%M")
                if slot_str not in booked_times:
                    available_slots.append(slot_str)
            slot_count += 1
            current += timedelta(minutes=schedule.slot_duration_min)

    available_slots.sort()
    return AvailableSlotsResponse(doctor_id=doctor_id, date=str(date), slots=available_slots)


# ── Leave Request endpoints ────────────────────────────────────────────────

@router.post("/me/leaves", response_model=LeaveRequestResponse, status_code=201)
async def create_leave_request(
    data: LeaveRequestCreate,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ đăng ký nghỉ phép"""
    result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bác sĩ")

    # Check if already has a leave for this date
    existing = await db.execute(
        select(LeaveRequest).where(
            LeaveRequest.doctor_id == doctor.id,
            LeaveRequest.leave_date == data.leave_date
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bạn đã đăng ký nghỉ ngày này rồi")

    leave = LeaveRequest(
        doctor_id=doctor.id,
        leave_date=data.leave_date,
        reason=data.reason,
        status="APPROVED"  # Auto-approved as requested
    )
    db.add(leave)
    await db.commit()
    await db.refresh(leave)
    return leave


@router.get("/me/leaves", response_model=List[LeaveRequestResponse])
async def get_my_leaves(
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ xem danh sách nghỉ phép của mình"""
    result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bác sĩ")

    result = await db.execute(
        select(LeaveRequest)
        .where(LeaveRequest.doctor_id == doctor.id)
        .order_by(LeaveRequest.leave_date.desc())
    )
    return result.scalars().all()


@router.delete("/me/leaves/{leave_id}", status_code=204)
async def delete_leave(
    leave_id: UUID,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ xóa/hủy lịch nghỉ phép"""
    result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bác sĩ")

    result = await db.execute(
        select(LeaveRequest).where(
            LeaveRequest.id == leave_id,
            LeaveRequest.doctor_id == doctor.id
        )
    )
    leave = result.scalar_one_or_none()
    if not leave:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch nghỉ phép")

    await db.delete(leave)
    await db.commit()
    return None


# ── Patient Management (for Doctors) ───────────────────────────────────────

@router.get("/patients/{patient_id}/history")
async def get_patient_history(
    patient_id: UUID,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Bác sĩ xem lịch sử khám bệnh của một bệnh nhân"""
    query = (
        select(Appointment)
        .where(Appointment.patient_id == patient_id, Appointment.status == "COMPLETED")
        .order_by(Appointment.scheduled_date.desc())
    )
    result = await db.execute(query)
    appointments = result.scalars().all()
    
    history = []
    for appt in appointments:
        # Get doctor name
        dr_result = await db.execute(
            select(User).join(Doctor, Doctor.user_id == User.id).where(Doctor.id == appt.doctor_id)
        )
        doctor_user = dr_result.scalar_one_or_none()
        
        # Get prescription clinical data
        presc_result = await db.execute(select(Prescription).where(Prescription.appointment_id == appt.id))
        presc = presc_result.scalar_one_or_none()
        
        history.append({
            "id": appt.id,
            "date": appt.scheduled_date,
            "time": appt.scheduled_time,
            "reason": appt.reason,
            "doctor_notes": appt.doctor_notes,
            "doctor_name": doctor_user.full_name if doctor_user else "Bác sĩ",
            "clinical_data": {
                "age": presc.patient_age if presc else None,
                "weight": presc.patient_weight if presc else None,
                "height": presc.patient_height if presc else None,
                "address": presc.patient_address if presc else None,
                "diagnosis": presc.diagnosis if presc else None,
                "advice": presc.advice if presc else None
            } if presc else None
        })
    return history
