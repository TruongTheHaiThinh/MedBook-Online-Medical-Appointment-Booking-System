"""
AppointmentService – State Machine, QR generation, slot booking with race condition protection.
"""
import uuid as uuid_mod
from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional

from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.appointment import Appointment, Payment
from app.models.doctor import Doctor
from app.models.user import User
from app.models.specialty import Specialty
from app.core.email import send_appointment_email

# Valid state transitions
VALID_TRANSITIONS = {
    "AWAITING_PAYMENT": ["PENDING", "CONFIRMED", "CANCELLED"],
    "PENDING": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["IN_PROGRESS", "CANCELLED"],
    "IN_PROGRESS": ["PRESCRIPTION_SENT"],
    "PRESCRIPTION_SENT": ["COMPLETED"],
    "COMPLETED": [],
    "CANCELLED": [],
}


def _generate_qr_token() -> str:
    import random, string
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"MB-{code}"


class AppointmentService:

    @staticmethod
    async def create(
        patient: User,
        doctor_id: UUID,
        scheduled_date,
        scheduled_time,
        reason: Optional[str],
        db: AsyncSession,
        background_tasks: BackgroundTasks,
    ) -> Appointment:
        if scheduled_date < datetime.now().date():
            raise HTTPException(status_code=400, detail="Không thể đặt lịch trong quá khứ")

        # Verify doctor
        result = await db.execute(
            select(Doctor, User)
            .join(User, Doctor.user_id == User.id)
            .where(Doctor.id == doctor_id, Doctor.is_approved == True)
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Bác sĩ không tồn tại hoặc chưa được phê duyệt")
        doctor, doctor_user = row

        # Race condition protection with SELECT FOR UPDATE
        async with db.begin_nested():
            # Check patient double-booking
            r1 = await db.execute(
                select(Appointment).where(
                    Appointment.patient_id == patient.id,
                    Appointment.scheduled_date == scheduled_date,
                    Appointment.scheduled_time == scheduled_time,
                    Appointment.status.in_(["AWAITING_PAYMENT", "PENDING", "CONFIRMED", "IN_PROGRESS"]),
                ).with_for_update()
            )
            if r1.scalar_one_or_none():
                raise HTTPException(status_code=409, detail="Bạn đã có lịch hẹn khác vào cùng giờ này")

            # Check doctor slot
            r2 = await db.execute(
                select(Appointment).where(
                    Appointment.doctor_id == doctor_id,
                    Appointment.scheduled_date == scheduled_date,
                    Appointment.scheduled_time == scheduled_time,
                    Appointment.status.in_(["AWAITING_PAYMENT", "PENDING", "CONFIRMED", "IN_PROGRESS"]),
                ).with_for_update()
            )
            if r2.scalar_one_or_none():
                raise HTTPException(status_code=409, detail="Slot này đã được đặt, vui lòng chọn giờ khác")

            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor_id,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                reason=reason,
                status="AWAITING_PAYMENT",
                qr_code=None, # Sẽ sinh sau khi thanh toán
            )
            db.add(appointment)

            await db.flush() # Lấy ID của appointment

            # Tạo bản ghi thanh toán 100k
            payment = Payment(
                appointment_id=appointment.id,
                amount=100000.0,
                payment_method="transfer",
                status="PENDING"
            )
            db.add(payment)

        await db.commit()
        await db.refresh(appointment)

        # Email notification
        if patient.email:
            background_tasks.add_task(
                send_appointment_email,
                to_email=patient.email,
                title="Đặt lịch hẹn – Chờ thanh toán",
                message="Lịch hẹn của bạn đã được khởi tạo. Vui lòng thanh toán 100,000 VNĐ để hoàn tất đặt lịch.",
                patient_name=patient.full_name,
                doctor_name=doctor_user.full_name,
                scheduled_date=str(scheduled_date),
                scheduled_time=str(scheduled_time),
                reason=reason,
            )

        return appointment

    @staticmethod
    def validate_transition(current_status: str, new_status: str):
        allowed = VALID_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Không thể chuyển từ {current_status} sang {new_status}. "
                       f"Trạng thái hợp lệ: {', '.join(allowed) if allowed else 'không có'}",
            )

    @staticmethod
    async def transition(
        appointment_id: UUID,
        new_status: str,
        db: AsyncSession,
        actor: User,
        notes: Optional[str] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> Appointment:
        result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
        appointment = result.scalar_one_or_none()
        if not appointment:
            raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")

        AppointmentService.validate_transition(appointment.status, new_status)

        # Role-based authorization
        if new_status == "CONFIRMED" and actor.role not in ["cashier_admin", "hr_admin"]:
            raise HTTPException(status_code=403, detail="Chỉ thu ngân mới có quyền xác nhận lịch hẹn")
        if new_status == "IN_PROGRESS" and actor.role not in ["cashier_admin", "hr_admin"]:
            raise HTTPException(status_code=403, detail="Chỉ thu ngân mới có quyền check-in bệnh nhân")
        if new_status == "PRESCRIPTION_SENT" and actor.role != "doctor":
            raise HTTPException(status_code=403, detail="Chỉ bác sĩ mới gửi đơn thuốc")
        if new_status == "COMPLETED" and actor.role not in ["cashier_admin", "hr_admin"]:
            raise HTTPException(status_code=403, detail="Chỉ thu ngân mới có quyền hoàn thành ca khám")
        if new_status == "CANCELLED":
            if actor.role == "patient" and appointment.patient_id != actor.id:
                raise HTTPException(status_code=403, detail="Không có quyền hủy lịch này")
            # if actor.role == "patient":
            #     scheduled_dt = datetime.combine(appointment.scheduled_date, appointment.scheduled_time)
            #     if datetime.now() > scheduled_dt - timedelta(hours=24):
            #         raise HTTPException(status_code=400, detail="Chỉ được hủy lịch trước 24 giờ")

        # Assign Queue Number and Room Number when confirmed
        if new_status == "CONFIRMED":
            # Get max queue number for this doctor on this day
            if not appointment.queue_number:
                q_stmt = select(func.max(Appointment.queue_number)).where(
                    Appointment.doctor_id == appointment.doctor_id,
                    Appointment.scheduled_date == appointment.scheduled_date
                )
                max_q = (await db.execute(q_stmt)).scalar() or 0
                appointment.queue_number = max_q + 1
            
            # Auto-assign room from doctor profile
            if not appointment.room_number:
                dr_res = await db.execute(select(Doctor).where(Doctor.id == appointment.doctor_id))
                doctor_obj = dr_res.scalar_one_or_none()
                if doctor_obj:
                    appointment.room_number = doctor_obj.room_number

        appointment.status = new_status
        if notes:
            appointment.doctor_notes = notes

        await db.commit()
        await db.refresh(appointment)

        # Email notification
        if background_tasks:
            pt_result = await db.execute(select(User).where(User.id == appointment.patient_id))
            patient = pt_result.scalar_one_or_none()
            dr_result = await db.execute(
                select(User).join(Doctor, Doctor.user_id == User.id).where(Doctor.id == appointment.doctor_id)
            )
            doctor_user = dr_result.scalar_one_or_none()

            status_titles = {
                "CONFIRMED": "Lịch hẹn đã được xác nhận",
                "CANCELLED": "Lịch hẹn đã bị hủy",
                "COMPLETED": "Ca khám đã hoàn thành",
            }
            title = status_titles.get(new_status)
            if title and patient and patient.email:
                background_tasks.add_task(
                    send_appointment_email,
                    to_email=patient.email,
                    title=title,
                    message=f"Trạng thái lịch hẹn: {new_status}",
                    patient_name=patient.full_name,
                    doctor_name=doctor_user.full_name if doctor_user else "Bác sĩ",
                    scheduled_date=str(appointment.scheduled_date),
                    scheduled_time=str(appointment.scheduled_time),
                    doctor_notes=notes,
                )

        return appointment

    @staticmethod
    async def checkin_by_qr(qr_code: str, db: AsyncSession, cashier: User) -> Appointment:
        """Check-in bệnh nhân bằng mã QR hoặc ID"""
        from sqlalchemy import cast, String as SAString, func, or_
        clean_code = qr_code.strip().lower()
        
        print(f"DEBUG: Checking in with code: '{clean_code}'")
        
        # Tìm kiếm cực kỳ linh hoạt
        stmt = select(Appointment).where(
            or_(
                func.lower(cast(Appointment.id, SAString)).contains(clean_code),
                func.lower(Appointment.qr_code).contains(clean_code)
            )
        )
        result = await db.execute(stmt)
        appointment = result.scalars().first()
        
        if not appointment:
            print(f"DEBUG: Appointment not found for code: '{clean_code}'")
            raise HTTPException(status_code=404, detail=f"Không tìm thấy lịch hẹn với mã: {qr_code}")

        await AppointmentService.transition(appointment.id, "IN_PROGRESS", db, cashier)
        
        # Gán số phòng mặc định nếu chưa có
        if not appointment.room_number:
            appointment.room_number = "Phòng 101 (Tầng 1)"
            
        await db.commit()
        await db.refresh(appointment)
        return appointment

    @staticmethod
    async def pay(appointment_id: UUID, db: AsyncSession, patient: User) -> Appointment:
        """Bệnh nhân thực hiện thanh toán (Simulated): AWAITING_PAYMENT -> CONFIRMED (Auto-approve)"""
        result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
        appointment = result.scalar_one_or_none()
        if not appointment:
            raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")
        
        if appointment.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Không có quyền thanh toán cho lịch hẹn này")
            
        if appointment.status != "AWAITING_PAYMENT":
            raise HTTPException(status_code=400, detail="Lịch hẹn không ở trạng thái chờ thanh toán")
        
        # Cập nhật Payment
        pay_res = await db.execute(select(Payment).where(Payment.appointment_id == appointment_id))
        payment = pay_res.scalar_one_or_none()
        if payment:
            payment.status = "PAID"
            payment.payment_method = "VNPAY"
            payment.paid_at = datetime.now()
        
        # Tự động duyệt: Chuyển trạng thái Appointment sang CONFIRMED
        appointment.status = "CONFIRMED"
        
        # Cấp số thứ tự và phòng khám
        if not appointment.queue_number:
            q_stmt = select(func.max(Appointment.queue_number)).where(
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.scheduled_date == appointment.scheduled_date
            )
            max_q = (await db.execute(q_stmt)).scalar() or 0
            appointment.queue_number = max_q + 1
        
        if not appointment.room_number:
            dr_res = await db.execute(select(Doctor).where(Doctor.id == appointment.doctor_id))
            doctor_obj = dr_res.scalar_one_or_none()
            if doctor_obj:
                appointment.room_number = doctor_obj.room_number

        # Sau khi thanh toán mới cấp mã QR định danh lịch hẹn
        appointment.qr_code = _generate_qr_token()
        
        await db.commit()
        await db.refresh(appointment)
        return appointment
