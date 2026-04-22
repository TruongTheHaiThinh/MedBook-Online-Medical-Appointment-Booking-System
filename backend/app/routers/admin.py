from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.specialty import Specialty
from app.models.appointment import Appointment
from app.schemas.doctor import SpecialtyCreate, SpecialtyUpdate, SpecialtyResponse, DoctorProfileResponse
from app.schemas.user import UserResponse
from app.core.security import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Specialties CRUD ──────────────────────────────────────────────────────────

@router.get("/specialties", response_model=List[SpecialtyResponse])
async def list_specialties(db: AsyncSession = Depends(get_db)):
    """Danh sách tất cả chuyên khoa (public)"""
    result = await db.execute(select(Specialty))
    return result.scalars().all()


@router.post("/specialties", response_model=SpecialtyResponse, status_code=201)
async def create_specialty(
    data: SpecialtyCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin tạo chuyên khoa mới"""
    result = await db.execute(select(Specialty).where(Specialty.name == data.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Tên chuyên khoa đã tồn tại")

    specialty = Specialty(name=data.name, description=data.description)
    db.add(specialty)
    await db.commit()
    await db.refresh(specialty)
    return specialty


@router.patch("/specialties/{specialty_id}", response_model=SpecialtyResponse)
async def update_specialty(
    specialty_id: UUID,
    data: SpecialtyUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Specialty).where(Specialty.id == specialty_id))
    specialty = result.scalar_one_or_none()
    if not specialty:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyên khoa")

    if data.name:
        # Check uniqueness
        other = await db.execute(
            select(Specialty).where(Specialty.name == data.name, Specialty.id != specialty_id)
        )
        if other.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Tên chuyên khoa đã tồn tại")
        specialty.name = data.name
    if data.description is not None:
        specialty.description = data.description

    await db.commit()
    await db.refresh(specialty)
    return specialty


@router.delete("/specialties/{specialty_id}", status_code=204)
async def delete_specialty(
    specialty_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Specialty).where(Specialty.id == specialty_id))
    specialty = result.scalar_one_or_none()
    if not specialty:
        raise HTTPException(status_code=404, detail="Không tìm thấy chuyên khoa")

    # Check if doctors still use this specialty
    dr_result = await db.execute(select(Doctor).where(Doctor.specialty_id == specialty_id, Doctor.is_approved == True))
    if dr_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Không thể xóa chuyên khoa đang có bác sĩ hoạt động")

    await db.delete(specialty)
    await db.commit()


# ── Doctor Approval ───────────────────────────────────────────────────────────

@router.get("/doctors/pending", response_model=List[DoctorProfileResponse])
async def list_pending_doctors(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin xem danh sách bác sĩ chờ phê duyệt"""
    result = await db.execute(
        select(Doctor, User, Specialty)
        .join(User, Doctor.user_id == User.id)
        .outerjoin(Specialty, Doctor.specialty_id == Specialty.id)
        .where(Doctor.is_approved == False)
    )
    rows = result.all()
    return [
        DoctorProfileResponse(
            id=d.id, user_id=d.user_id, specialty_id=d.specialty_id,
            bio=d.bio, experience_years=d.experience_years, is_approved=d.is_approved,
            full_name=u.full_name, email=u.email,
            specialty_name=s.name if s else None,
        )
        for d, u, s in rows
    ]


@router.patch("/doctors/{doctor_id}/approve", response_model=DoctorProfileResponse)
async def approve_doctor(
    doctor_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin phê duyệt tài khoản bác sĩ"""
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

    doctor.is_approved = True
    await db.commit()
    await db.refresh(doctor)

    return DoctorProfileResponse(
        id=doctor.id, user_id=doctor.user_id, specialty_id=doctor.specialty_id,
        bio=doctor.bio, experience_years=doctor.experience_years, is_approved=True,
        full_name=user.full_name, email=user.email,
        specialty_name=specialty.name if specialty else None,
    )


@router.patch("/doctors/{doctor_id}/reject")
async def reject_doctor(
    doctor_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin từ chối tài khoản bác sĩ"""
    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy bác sĩ")

    dr_user_result = await db.execute(select(User).where(User.id == doctor.user_id))
    user = dr_user_result.scalar_one_or_none()
    if user:
        user.is_active = False

    await db.commit()
    return {"message": "Đã từ chối và vô hiệu hóa tài khoản bác sĩ"}


# ── User Management ───────────────────────────────────────────────────────────

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    role: str = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin xem danh sách tất cả người dùng"""
    query = select(User)
    if role:
        query = query.where(User.role == role)
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin khóa/mở khóa tài khoản người dùng"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Không thể tự khóa tài khoản của mình")

    user.is_active = not user.is_active
    await db.commit()
    return {"message": f"Tài khoản đã được {'mở khóa' if user.is_active else 'khóa'}", "is_active": user.is_active}


# ── Statistics ────────────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin xem thống kê hệ thống"""
    total_patients = await db.execute(select(func.count(User.id)).where(User.role == "patient"))
    total_doctors = await db.execute(select(func.count(User.id)).where(User.role == "doctor"))
    total_appointments = await db.execute(select(func.count(Appointment.id)))

    status_counts = {}
    for status in ["PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"]:
        count_result = await db.execute(
            select(func.count(Appointment.id)).where(Appointment.status == status)
        )
        status_counts[status] = count_result.scalar()

    # Last 30 days appointments history (line chart)
    from datetime import date, timedelta
    thirty_days_ago = date.today() - timedelta(days=30)
    
    history_result = await db.execute(
        select(Appointment.scheduled_date, func.count(Appointment.id))
        .where(Appointment.scheduled_date >= thirty_days_ago)
        .group_by(Appointment.scheduled_date)
        .order_by(Appointment.scheduled_date.asc())
    )
    history_data = history_result.all()
    
    # Fill gaps for days with 0 appointments
    history_map = {row[0]: row[1] for row in history_data}
    chart_data = []
    for i in range(31):
        d = thirty_days_ago + timedelta(days=i)
        chart_data.append({
            "date": str(d),
            "count": history_map.get(d, 0)
        })

    return {
        "total_patients": total_patients.scalar(),
        "total_doctors": total_doctors.scalar(),
        "total_appointments": total_appointments.scalar(),
        "appointments_by_status": status_counts,
        "appointments_history": chart_data,
    }
