from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, and_
from datetime import date, timedelta
import asyncio

from app.database import AsyncSessionLocal
from app.models.appointment import Appointment
from app.models.user import User
from app.models.doctor import Doctor
from app.core.email import send_appointment_email

async def send_reminders():
    """Background task to send reminders for appointments in the next 24-48 hours"""
    async with AsyncSessionLocal() as db:
        # Looking for CONFIRMED appointments scheduled for tomorrow that haven't had a reminder
        tomorrow = date.today() + timedelta(days=1)
        
        result = await db.execute(
            select(Appointment).where(
                Appointment.status == "CONFIRMED",
                Appointment.scheduled_date == tomorrow,
                Appointment.reminder_sent == False
            )
        )
        appointments = result.scalars().all()
        
        for appt in appointments:
            # Get patient info
            pt_res = await db.execute(select(User).where(User.id == appt.patient_id))
            patient = pt_res.scalar_one_or_none()
            
            # Get doctor info
            dr_res = await db.execute(
                select(User).join(Doctor, Doctor.user_id == User.id).where(Doctor.id == appt.doctor_id)
            )
            doctor_user = dr_res.scalar_one_or_none()
            
            if patient and doctor_user:
                try:
                    await send_appointment_email(
                        to_email=patient.email,
                        title="Nhắc hẹn ngày mai",
                        message=f"Đây là tin nhắn nhắc lịch hẹn khám bệnh của bạn vào ngày mai.",
                        patient_name=patient.full_name,
                        doctor_name=doctor_user.full_name,
                        scheduled_date=str(appt.scheduled_date),
                        scheduled_time=str(appt.scheduled_time),
                        reason=appt.reason
                    )
                    appt.reminder_sent = True
                except Exception as e:
                    print(f"[SCHEDULER ERROR] Could not send reminder for appt {appt.id}: {e}")

        await db.commit()

def start_scheduler():
    scheduler = AsyncIOScheduler()
    # Runs every 4 hours to check for upcoming appointments
    scheduler.add_job(send_reminders, "interval", hours=4)
    scheduler.start()
    print("[SCHEDULER STARTED] Automated appointment reminders are active.")
