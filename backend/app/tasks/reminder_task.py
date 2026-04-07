"""
APScheduler background job: send reminder emails 24h before appointments.
Runs every hour, scans CONFIRMED appointments without reminder_sent=True.
"""
import logging
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.database import AsyncSessionLocal
from app.repositories.appointment_repo import AppointmentRepository
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def send_reminders():
    """Check for appointments in the 24-25h window and send reminder emails."""
    logger.info("Running reminder job...")
    now = datetime.datetime.now()
    window_start = now + datetime.timedelta(hours=24)
    window_end = now + datetime.timedelta(hours=25)

    async with AsyncSessionLocal() as db:
        repo = AppointmentRepository(db)
        appointments = await repo.get_pending_reminders(window_start, window_end)

        email_service = EmailService()
        for appt in appointments:
            scheduled_dt = datetime.datetime.combine(appt.scheduled_date, appt.scheduled_time)
            if window_start <= scheduled_dt <= window_end:
                try:
                    await email_service.send_appointment_reminder(appt)
                    await repo.update(appt, reminder_sent=True)
                    logger.info("Reminder sent for appointment %s", appt.id)
                except Exception as e:
                    logger.error("Failed to send reminder for %s: %s", appt.id, e)


def start_scheduler():
    scheduler.add_job(send_reminders, "interval", hours=1, id="reminder_job")
    scheduler.start()
    logger.info("APScheduler started — reminder job every 1 hour")


def stop_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler stopped")
