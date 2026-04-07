from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import UserRole, User
from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def get_system_stats(
    current_user=Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Admin: Dashboard statistics – counts by status, new users, etc."""
    # Total users by role
    total_patients = (
        await db.execute(select(func.count(User.id)).where(User.role == UserRole.patient))
    ).scalar()
    total_doctors = (
        await db.execute(select(func.count(User.id)).where(User.role == UserRole.doctor))
    ).scalar()

    # Appointments by status
    pending = (
        await db.execute(
            select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.pending)
        )
    ).scalar()
    confirmed = (
        await db.execute(
            select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.confirmed)
        )
    ).scalar()
    cancelled = (
        await db.execute(
            select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.cancelled)
        )
    ).scalar()
    completed = (
        await db.execute(
            select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.completed)
        )
    ).scalar()

    return {
        "users": {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
        },
        "appointments": {
            "pending": pending,
            "confirmed": confirmed,
            "cancelled": cancelled,
            "completed": completed,
            "total": (pending or 0) + (confirmed or 0) + (cancelled or 0) + (completed or 0),
        },
    }


@router.get("/users")
async def list_all_users(
    current_user=Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Admin: List all users."""
    from app.repositories.user_repo import UserRepository
    repo = UserRepository(db)
    users, total = await repo.list_all()
    return {"users": users, "total": total}


@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user=Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Admin: Deactivate (lock) a user account."""
    from app.repositories.user_repo import UserRepository
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    await repo.update(user, is_active=False)
    return {"message": f"User {user_id} deactivated"}
