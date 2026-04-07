import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import UUID
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User
from app.repositories.appointment_repo import AppointmentRepository
from app.repositories.doctor_repo import DoctorRepository
from app.services.scheduling_engine import SchedulingEngine
from app.services.email_service import EmailService
from app.schemas.appointment import AppointmentCreate


class AppointmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AppointmentRepository(db)
        self.doctor_repo = DoctorRepository(db)
        self.engine = SchedulingEngine(db)
        self.email_service = EmailService()

    async def create_appointment(
        self, patient: User, data: AppointmentCreate
    ) -> Appointment:
        # Validate doctor exists and is approved
        doctor = await self.doctor_repo.get_by_id(data.doctor_id)
        if not doctor or not doctor.is_approved:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found or not yet approved",
            )

        # Check patient doesn't have a conflicting appointment
        conflict = await self.repo.check_patient_conflict(
            patient.id, data.scheduled_date, data.scheduled_time
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have an appointment at this time",
            )

        # Race condition check: re-check slot availability inside the transaction
        async with self.db.begin_nested():
            booked = await self.repo.get_booked_times_for_slot(
                data.doctor_id, data.scheduled_date, data.scheduled_time
            )
            if booked:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Slot này vừa được đặt bởi người khác. Vui lòng chọn slot khác.",
                )

            appointment = await self.repo.create(
                patient_id=patient.id,
                doctor_id=data.doctor_id,
                scheduled_date=data.scheduled_date,
                scheduled_time=data.scheduled_time,
                reason=data.reason,
                status=AppointmentStatus.pending,
            )

        # Send confirmation email (async, non-blocking)
        await self.email_service.send_appointment_created(appointment, patient, doctor)
        return appointment

    async def confirm_appointment(self, doctor: User, appointment_id) -> Appointment:
        appointment = await self._get_and_validate_doctor_ownership(doctor, appointment_id)
        if appointment.status != AppointmentStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PENDING appointments can be confirmed",
            )
        updated = await self.repo.update(appointment, status=AppointmentStatus.confirmed)
        await self.email_service.send_appointment_confirmed(updated)
        return updated

    async def cancel_appointment_by_doctor(
        self, doctor: User, appointment_id, doctor_notes: str
    ) -> Appointment:
        if not doctor_notes or not doctor_notes.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Vui lòng cung cấp lý do hủy (doctor_notes bắt buộc)",
            )
        appointment = await self._get_and_validate_doctor_ownership(doctor, appointment_id)
        if appointment.status == AppointmentStatus.completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel a completed appointment",
            )
        updated = await self.repo.update(
            appointment, status=AppointmentStatus.cancelled, doctor_notes=doctor_notes
        )
        await self.email_service.send_appointment_cancelled(updated)
        return updated

    async def cancel_appointment_by_patient(
        self, patient: User, appointment_id
    ) -> Appointment:
        appointment = await self.repo.get_by_id(appointment_id)
        if not appointment or str(appointment.patient_id) != str(patient.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

        # 24-hour rule
        scheduled_dt = datetime.datetime.combine(
            appointment.scheduled_date, appointment.scheduled_time
        )
        now = datetime.datetime.now()
        if (scheduled_dt - now).total_seconds() < 24 * 3600:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ được hủy trước 24 giờ so với lịch hẹn",
            )

        updated = await self.repo.update(appointment, status=AppointmentStatus.cancelled)
        await self.email_service.send_appointment_cancelled(updated)
        return updated

    async def complete_appointment(self, doctor: User, appointment_id) -> Appointment:
        appointment = await self._get_and_validate_doctor_ownership(doctor, appointment_id)
        if appointment.status != AppointmentStatus.confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CONFIRMED appointments can be marked as completed",
            )
        return await self.repo.update(appointment, status=AppointmentStatus.completed)

    async def _get_and_validate_doctor_ownership(
        self, doctor: User, appointment_id
    ) -> Appointment:
        from app.repositories.doctor_repo import DoctorRepository
        doctor_profile = await DoctorRepository(self.db).get_by_user_id(doctor.id)
        if not doctor_profile:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a doctor")
        appointment = await self.repo.get_by_id(appointment_id)
        if not appointment or str(appointment.doctor_id) != str(doctor_profile.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
        return appointment
