import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import UserRole
from app.repositories.specialty_repo import SpecialtyRepository
from app.repositories.doctor_repo import DoctorRepository
from app.schemas.specialty import SpecialtyCreate, SpecialtyUpdate, SpecialtyResponse

router = APIRouter(prefix="/specialties", tags=["Specialties"])


@router.get("", response_model=list[SpecialtyResponse])
async def list_specialties(db: AsyncSession = Depends(get_db)):
    """Public: List all specialties."""
    repo = SpecialtyRepository(db)
    return await repo.list_all()


@router.post("", response_model=SpecialtyResponse, status_code=201)
async def create_specialty(
    data: SpecialtyCreate,
    current_user=Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Admin: Create a new specialty."""
    repo = SpecialtyRepository(db)
    existing = await repo.get_by_name(data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialty with this name already exists",
        )
    return await repo.create(name=data.name, description=data.description)


@router.patch("/{specialty_id}", response_model=SpecialtyResponse)
async def update_specialty(
    specialty_id: uuid.UUID,
    data: SpecialtyUpdate,
    current_user=Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Admin: Update a specialty."""
    repo = SpecialtyRepository(db)
    specialty = await repo.get_by_id(specialty_id)
    if not specialty:
        raise HTTPException(status_code=404, detail="Specialty not found")
    return await repo.update(specialty, name=data.name, description=data.description)


@router.delete("/{specialty_id}", status_code=204)
async def delete_specialty(
    specialty_id: uuid.UUID,
    current_user=Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Admin: Delete a specialty (only if no active doctors assigned)."""
    repo = SpecialtyRepository(db)
    specialty = await repo.get_by_id(specialty_id)
    if not specialty:
        raise HTTPException(status_code=404, detail="Specialty not found")

    # Guard: cannot delete if active doctors exist
    doctor_repo = DoctorRepository(db)
    doctors, _ = await doctor_repo.list_approved(specialty_id=specialty_id)
    if doctors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete specialty with active doctors assigned",
        )

    await repo.delete(specialty)
