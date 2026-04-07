"""
Email service using FastAPI-Mail + Jinja2 HTML templates.
Sends transactional emails for appointment lifecycle events.
"""
import logging
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"


class EmailService:
    def __init__(self):
        self._env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

    def _render(self, template_name: str, context: dict) -> str:
        try:
            template = self._env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            return ""

    async def _send(self, to_email: str, subject: str, html_body: str):
        """Send email using FastAPI-Mail. Gracefully skips if not configured."""
        try:
            from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
            from app.core.config import settings

            if not settings.MAIL_USERNAME:
                logger.warning("Email not configured — skipping send to %s", to_email)
                return

            conf = ConnectionConfig(
                MAIL_USERNAME=settings.MAIL_USERNAME,
                MAIL_PASSWORD=settings.MAIL_PASSWORD,
                MAIL_FROM=settings.MAIL_FROM,
                MAIL_PORT=settings.MAIL_PORT,
                MAIL_SERVER=settings.MAIL_SERVER,
                MAIL_STARTTLS=settings.MAIL_STARTTLS,
                MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
                USE_CREDENTIALS=True,
            )
            message = MessageSchema(
                subject=subject,
                recipients=[to_email],
                body=html_body,
                subtype=MessageType.html,
            )
            fm = FastMail(conf)
            await fm.send_message(message)
            logger.info("Email sent to %s — %s", to_email, subject)
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to_email, e)

    async def send_appointment_created(self, appointment, patient, doctor):
        html = self._render("appointment_created.html", {
            "patient_name": patient.full_name,
            "doctor_name": doctor.user.full_name if doctor.user else "Doctor",
            "date": str(appointment.scheduled_date),
            "time": str(appointment.scheduled_time),
        })
        await self._send(
            to_email=patient.email,
            subject="[MedBook] Đặt lịch thành công – Đang chờ xác nhận",
            html_body=html,
        )

    async def send_appointment_confirmed(self, appointment):
        html = self._render("appointment_confirmed.html", {
            "patient_name": appointment.patient.full_name if appointment.patient else "",
            "date": str(appointment.scheduled_date),
            "time": str(appointment.scheduled_time),
        })
        await self._send(
            to_email=appointment.patient.email,
            subject="[MedBook] Lịch hẹn đã được xác nhận!",
            html_body=html,
        )

    async def send_appointment_cancelled(self, appointment):
        html = self._render("appointment_cancelled.html", {
            "patient_name": appointment.patient.full_name if appointment.patient else "",
            "date": str(appointment.scheduled_date),
            "time": str(appointment.scheduled_time),
            "reason": appointment.doctor_notes or "Không có lý do cụ thể",
        })
        await self._send(
            to_email=appointment.patient.email,
            subject="[MedBook] Lịch hẹn đã bị hủy",
            html_body=html,
        )

    async def send_appointment_reminder(self, appointment):
        html = self._render("appointment_confirmed.html", {
            "patient_name": appointment.patient.full_name if appointment.patient else "",
            "date": str(appointment.scheduled_date),
            "time": str(appointment.scheduled_time),
        })
        await self._send(
            to_email=appointment.patient.email,
            subject="[MedBook] Nhắc lịch khám – Còn 24 giờ nữa",
            html_body=html,
        )
