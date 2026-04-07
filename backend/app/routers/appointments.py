import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import UserRole
from app.models.appointment import AppointmentStatus
from app.services.appointment_service import AppointmentService
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentCancel,
    AppointmentResponse,
    PaginatedAppointments,
)
from app.repositories.appointment_repo import AppointmentRepository
import math

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    data: AppointmentCreate,
    current_user=Depends(require_role(UserRole.patient)),
    db: AsyncSession = Depends(get_db),
):
    """Patient: Book a new appointment."""
    service = AppointmentService(db)
    return await service.create_appointment(current_user, data)


@router.get("/me", response_model=PaginatedAppointments)
async def get_my_appointments(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Patient or Doctor: Get own appointments history."""
    repo = AppointmentRepository(db)
    if current_user.role == UserRole.patient:
        items, total = await repo.list_for_patient(current_user.id, page=page, size=size)
    else:
        from app.repositories.doctor_repo import DoctorRepository
        doctor = await DoctorRepository(db).get_by_user_id(current_user.id)
        items, total = await repo.list_for_doctor(doctor.id, page=page, size=size)

    return PaginatedAppointments(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )


@router.patch("/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(
    appointment_id: uuid.UUID,
    current_user=Depends(require_role(UserRole.doctor)),
    db: AsyncSession = Depends(get_db),
):
    """Doctor: Confirm a PENDING appointment."""
    service = AppointmentService(db)
    return await service.confirm_appointment(current_user, appointment_id)


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: uuid.UUID,
    data: AppointmentCancel = AppointmentCancel(),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Patient or Doctor: Cancel an appointment. Doctor must provide doctor_notes."""
    service = AppointmentService(db)
    if current_user.role == UserRole.doctor:
        return await service.cancel_appointment_by_doctor(
            current_user, appointment_id, data.doctor_notes or ""
        )
    else:
        return await service.cancel_appointment_by_patient(current_user, appointment_id)


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
async def complete_appointment(
    appointment_id: uuid.UUID,
    current_user=Depends(require_role(UserRole.doctor)),
    db: AsyncSession = Depends(get_db),
):
    """Doctor: Mark a CONFIRMED appointment as COMPLETED after visit."""
    service = AppointmentService(db)
    return await service.complete_appointment(current_user, appointment_id)
