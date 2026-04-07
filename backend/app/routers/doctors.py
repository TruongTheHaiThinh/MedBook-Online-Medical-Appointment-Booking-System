from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import UserRole
from app.repositories.doctor_repo import DoctorRepository
from app.repositories.specialty_repo import SpecialtyRepository
from app.schemas.doctor import DoctorUpdateProfile, DoctorPublicResponse, DoctorResponse
from app.services.scheduling_engine import SchedulingEngine
from app.schemas.schedule import AvailableSlot
import datetime
import uuid

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("", response_model=list[DoctorPublicResponse])
async def list_doctors(
    specialty_id: uuid.UUID | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint: list approved doctors, optionally filtered by specialty."""
    repo = DoctorRepository(db)
    doctors, _ = await repo.list_approved(specialty_id=specialty_id, page=page, size=size)
    return [
        DoctorPublicResponse(
            id=d.id,
            full_name=d.user.full_name,
            specialty=d.specialty,
            experience_years=d.experience_years,
            bio=d.bio,
        )
        for d in doctors
    ]


@router.get("/{doctor_id}/available-slots", response_model=list[AvailableSlot])
async def get_available_slots(
    doctor_id: uuid.UUID,
    date: datetime.date = Query(..., description="Date in YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
):
    """Public: Get available appointment slots for a doctor on a given date."""
    engine = SchedulingEngine(db)
    return await engine.get_available_slots(doctor_id, date)


@router.get("/me", response_model=DoctorResponse)
async def get_my_profile(
    current_user=Depends(require_role(UserRole.doctor)),
    db: AsyncSession = Depends(get_db),
):
    """Doctor: Get own profile."""
    repo = DoctorRepository(db)
    doctor = await repo.get_by_user_id(current_user.id)
    return doctor


@router.patch("/me", response_model=DoctorResponse)
async def update_my_profile(
    data: DoctorUpdateProfile,
    current_user=Depends(require_role(UserRole.doctor)),
    db: AsyncSession = Depends(get_db),
):
    """Doctor: Update own profile (bio, experience, specialty)."""
    repo = DoctorRepository(db)
    doctor = await repo.get_by_user_id(current_user.id)
    updated = await repo.update(
        doctor,
        bio=data.bio,
        experience_years=data.experience_years,
        specialty_id=data.specialty_id,
    )
    return updated


# Admin actions
@router.get("/pending-approval", response_model=list[DoctorResponse])
async def list_pending_doctors(
    current_user=Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Admin: List doctor accounts pending approval."""
    repo = DoctorRepository(db)
    doctors = await repo.list_pending_approval()
    return doctors


@router.patch("/{doctor_id}/approve")
async def approve_doctor(
    doctor_id: uuid.UUID,
    current_user=Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Admin: Approve a doctor account."""
    repo = DoctorRepository(db)
    doctor = await repo.get_by_id(doctor_id)
    updated = await repo.update(doctor, is_approved=True)
    return {"message": "Doctor approved", "doctor_id": str(updated.id)}


@router.patch("/{doctor_id}/reject")
async def reject_doctor(
    doctor_id: uuid.UUID,
    current_user=Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Admin: Reject (deactivate) a doctor account."""
    from app.repositories.user_repo import UserRepository
    repo = DoctorRepository(db)
    doctor = await repo.get_by_id(doctor_id)
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(doctor.user_id)
    await user_repo.update(user, is_active=False)
    return {"message": "Doctor rejected and account deactivated"}
