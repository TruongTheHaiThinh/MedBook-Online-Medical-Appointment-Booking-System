"""
MedicalService – Medical records and prescription management.
"""
from uuid import UUID
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.appointment import Appointment, MedicalRecord, PrescriptionItem
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.appointment import MedicalRecordCreate


class MedicalService:

    @staticmethod
    async def create_record(
        data: MedicalRecordCreate,
        doctor_user: User,
        db: AsyncSession,
    ) -> MedicalRecord:
        """Doctor creates medical record + prescription items for an appointment."""
        # Get doctor profile
        dr_result = await db.execute(select(Doctor).where(Doctor.user_id == doctor_user.id))
        doctor = dr_result.scalar_one_or_none()
        if not doctor:
            raise HTTPException(status_code=403, detail="Không tìm thấy hồ sơ bác sĩ")

        # Verify appointment belongs to this doctor and is IN_PROGRESS
        appt_result = await db.execute(
            select(Appointment).where(
                Appointment.id == data.appointment_id,
                Appointment.doctor_id == doctor.id,
            )
        )
        appointment = appt_result.scalar_one_or_none()
        if not appointment:
            raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")

        if appointment.status not in ["IN_PROGRESS", "CONFIRMED"]:
            raise HTTPException(
                status_code=400,
                detail=f"Chỉ có thể tạo hồ sơ cho lịch hẹn IN_PROGRESS hoặc CONFIRMED, hiện tại: {appointment.status}",
            )

        # Check if record already exists
        existing = await db.execute(
            select(MedicalRecord).where(MedicalRecord.appointment_id == data.appointment_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Lịch hẹn này đã có hồ sơ khám bệnh")

        # Create medical record
        record = MedicalRecord(
            appointment_id=data.appointment_id,
            patient_id=appointment.patient_id,
            doctor_id=doctor.id,
            diagnosis=data.diagnosis,
            notes=data.notes,
            revisit_required=data.revisit_required,
            revisit_date=data.revisit_date,
        )
        db.add(record)
        await db.flush()

        # Create prescription items
        for item_data in data.prescriptions:
            item = PrescriptionItem(
                medical_record_id=record.id,
                medicine_name=item_data.medicine_name,
                dosage=item_data.dosage,
                frequency=item_data.frequency,
                duration=item_data.duration,
                morning=item_data.morning,
                noon=item_data.noon,
                afternoon=item_data.afternoon,
                evening=item_data.evening,
                total_quantity=item_data.total_quantity,
                instructions=item_data.instructions,
            )
            db.add(item)

        # Transition appointment to PRESCRIPTION_SENT only if final
        if data.is_final:
            appointment.status = "PRESCRIPTION_SENT"
        
        await db.commit()

        # Reload with prescriptions
        result = await db.execute(
            select(MedicalRecord)
            .options(selectinload(MedicalRecord.prescriptions))
            .where(MedicalRecord.id == record.id)
        )
        return result.scalar_one()

    @staticmethod
    async def update_record(
        appointment_id: UUID,
        data: MedicalRecordCreate,
        doctor_user: User,
        db: AsyncSession,
    ) -> MedicalRecord:
        """Doctor updates an existing medical record."""
        dr_result = await db.execute(select(Doctor).where(Doctor.user_id == doctor_user.id))
        doctor = dr_result.scalar_one_or_none()
        if not doctor:
            raise HTTPException(status_code=403, detail="Không tìm thấy hồ sơ bác sĩ")

        result = await db.execute(
            select(MedicalRecord)
            .options(selectinload(MedicalRecord.prescriptions))
            .where(MedicalRecord.appointment_id == appointment_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ khám bệnh")

        if record.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Không có quyền sửa hồ sơ của bác sĩ khác")

        record.diagnosis = data.diagnosis
        record.notes = data.notes
        record.revisit_required = data.revisit_required
        record.revisit_date = data.revisit_date

        # Replace prescription items
        from sqlalchemy import delete
        await db.execute(delete(PrescriptionItem).where(PrescriptionItem.medical_record_id == record.id))

        for item_data in data.prescriptions:
            item = PrescriptionItem(
                medical_record_id=record.id,
                medicine_name=item_data.medicine_name,
                dosage=item_data.dosage,
                frequency=item_data.frequency,
                duration=item_data.duration,
                morning=item_data.morning,
                noon=item_data.noon,
                afternoon=item_data.afternoon,
                evening=item_data.evening,
                total_quantity=item_data.total_quantity,
                instructions=item_data.instructions,
            )
            db.add(item)

        # If it was a draft and now it's final, update status
        if data.is_final:
            # Need to fetch the appointment again or use a join
            from app.models.appointment import Appointment
            stmt = select(Appointment).where(Appointment.id == appointment_id)
            appt_res = await db.execute(stmt)
            appt = appt_res.scalar_one_or_none()
            if appt:
                appt.status = "PRESCRIPTION_SENT"

        await db.commit()

        # Reload
        result = await db.execute(
            select(MedicalRecord)
            .options(selectinload(MedicalRecord.prescriptions))
            .where(MedicalRecord.id == record.id)
        )
        return result.scalar_one()

    @staticmethod
    async def get_by_appointment(appointment_id: UUID, db: AsyncSession) -> MedicalRecord:
        stmt = (
            select(MedicalRecord)
            .options(
                selectinload(MedicalRecord.prescriptions),
                selectinload(MedicalRecord.doctor).selectinload(Doctor.user)
            )
            .where(MedicalRecord.appointment_id == appointment_id)
        )
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ khám bệnh")
        
        if record.doctor and record.doctor.user:
            record.doctor_name = record.doctor.user.full_name
            
        return record

    @staticmethod
    async def get_patient_history(patient_id: UUID, db: AsyncSession) -> List[MedicalRecord]:
        stmt = (
            select(MedicalRecord)
            .options(
                selectinload(MedicalRecord.prescriptions),
                selectinload(MedicalRecord.doctor).selectinload(Doctor.user)
            )
            .where(MedicalRecord.patient_id == patient_id)
            .order_by(MedicalRecord.created_at.desc())
        )
        result = await db.execute(stmt)
        records = result.scalars().all()
        for r in records:
            if r.doctor and r.doctor.user:
                r.doctor_name = r.doctor.user.full_name
        return records
