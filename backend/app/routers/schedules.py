import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import UserRole
from app.repositories.schedule_repo import ScheduleRepository
from app.repositories.doctor_repo import DoctorRepository
from app.schemas.schedule import ScheduleCreate, ScheduleResponse

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.get("/me", response_model=list[ScheduleResponse])
async def get_my_schedules(
    current_user=Depends(require_role(UserRole.doctor)),
    db: AsyncSession = Depends(get_db),
):
    """Doctor: Get own weekly schedule patterns."""
    doctor_repo = DoctorRepository(db)
    doctor = await doctor_repo.get_by_user_id(current_user.id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    repo = ScheduleRepository(db)
    return await repo.get_by_doctor(doctor.id)


@router.post("/me", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    data: ScheduleCreate,
    current_user=Depends(require_role(UserRole.doctor)),
    db: AsyncSession = Depends(get_db),
):
    """Doctor: Create a new weekly schedule pattern for a specific day."""
    doctor_repo = DoctorRepository(db)
    doctor = await doctor_repo.get_by_user_id(current_user.id)
    if not doctor or not doctor.is_approved:
        raise HTTPException(status_code=403, detail="Doctor must be approved to set schedules")

    repo = ScheduleRepository(db)
    # Check no duplicate for same day
    existing = await repo.get_by_doctor_and_day(doctor.id, data.day_of_week)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"A schedule already exists for day {data.day_of_week}. Please update or delete it first.",
        )

    # Validate slot duration divides working hours evenly
    from datetime import datetime, timedelta
    start = datetime.combine(datetime.today(), data.start_time)
    end = datetime.combine(datetime.today(), data.end_time)
    total_minutes = int((end - start).total_seconds() / 60)
    if total_minutes % data.slot_duration_min != 0:
        raise HTTPException(
            status_code=400,
            detail="slot_duration_min must evenly divide the (end_time - start_time) period",
        )

    return await repo.create(
        doctor_id=doctor.id,
        day_of_week=data.day_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
        slot_duration_min=data.slot_duration_min,
        max_slots=data.max_slots,
    )


@router.delete("/me/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: uuid.UUID,
    current_user=Depends(require_role(UserRole.doctor)),
    db: AsyncSession = Depends(get_db),
):
    """Doctor: Delete a schedule pattern."""
    doctor_repo = DoctorRepository(db)
    doctor = await doctor_repo.get_by_user_id(current_user.id)
    repo = ScheduleRepository(db)
    schedules = await repo.get_by_doctor(doctor.id)
    target = next((s for s in schedules if s.id == schedule_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await repo.delete(target)
