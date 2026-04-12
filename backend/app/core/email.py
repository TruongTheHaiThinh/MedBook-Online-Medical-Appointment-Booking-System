from typing import Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from jinja2 import Environment, BaseLoader

from app.config import settings

# Email templates
CONFIRM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
    <h1 style="color: white; margin: 0;">🏥 MedBook</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0;">Hệ thống đặt lịch khám bệnh trực tuyến</p>
  </div>
  <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 12px 12px;">
    <h2 style="color: #333;">{{ title }}</h2>
    <p style="color: #666;">Xin chào <strong>{{ patient_name }}</strong>,</p>
    <p style="color: #666;">{{ message }}</p>
    <div style="background: white; border-left: 4px solid #667eea; padding: 20px; border-radius: 8px; margin: 20px 0;">
      <p><strong>🩺 Bác sĩ:</strong> {{ doctor_name }}</p>
      <p><strong>📅 Ngày khám:</strong> {{ scheduled_date }}</p>
      <p><strong>⏰ Giờ khám:</strong> {{ scheduled_time }}</p>
      {% if reason %}<p><strong>📋 Lý do:</strong> {{ reason }}</p>{% endif %}
      {% if doctor_notes %}<p><strong>📝 Ghi chú:</strong> {{ doctor_notes }}</p>{% endif %}
    </div>
    <p style="color: #999; font-size: 14px; margin-top: 30px;">Email này được gửi tự động từ hệ thống MedBook. Vui lòng không trả lời email này.</p>
  </div>
</body>
</html>
"""


def _render_template(template_str: str, **kwargs) -> str:
    env = Environment(loader=BaseLoader())
    template = env.from_string(template_str)
    return template.render(**kwargs)


async def send_appointment_email(
    to_email: str,
    title: str,
    message: str,
    patient_name: str,
    doctor_name: str,
    scheduled_date: str,
    scheduled_time: str,
    reason: Optional[str] = None,
    doctor_notes: Optional[str] = None,
):
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        print(f"[EMAIL SKIPPED] To: {to_email} | {title}")
        return

    try:
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

        html_body = _render_template(
            CONFIRM_TEMPLATE,
            title=title,
            message=message,
            patient_name=patient_name,
            doctor_name=doctor_name,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            reason=reason,
            doctor_notes=doctor_notes,
        )

        msg = MessageSchema(
            subject=f"MedBook – {title}",
            recipients=[to_email],
            body=html_body,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(msg)
        print(f"[EMAIL SENT] To: {to_email} | {title}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
