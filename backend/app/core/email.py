from typing import Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from jinja2 import Environment, BaseLoader

from app.config import settings

# ── Base email layout ──
BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
    <h1 style="color: white; margin: 0;">🏥 MedBook</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0;">Hệ thống quản lý & đặt lịch khám bệnh trực tuyến</p>
  </div>
  <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 12px 12px;">
    {{ content }}
    <p style="color: #999; font-size: 14px; margin-top: 30px;">Email này được gửi tự động từ hệ thống MedBook. Vui lòng không trả lời email này.</p>
  </div>
</body>
</html>
"""

# ── Appointment notification ──
APPOINTMENT_CONTENT = """
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
"""

# ── Email verification ──
VERIFY_EMAIL_CONTENT = """
<h2 style="color: #333;">Xác thực tài khoản</h2>
<p style="color: #666;">Xin chào <strong>{{ full_name }}</strong>,</p>
<p style="color: #666;">Cảm ơn bạn đã đăng ký tài khoản MedBook. Vui lòng nhấn nút bên dưới để xác thực email của bạn:</p>
<div style="text-align: center; margin: 30px 0;">
  <a href="{{ verify_url }}" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 14px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
    ✅ Xác thực Email
  </a>
</div>
<p style="color: #999; font-size: 13px;">Hoặc copy đường link sau vào trình duyệt:<br><code>{{ verify_url }}</code></p>
<p style="color: #999; font-size: 13px;">Link có hiệu lực trong {{ expire_hours }} giờ.</p>
"""

# ── Password reset ──
RESET_PASSWORD_CONTENT = """
<h2 style="color: #333;">Đặt lại mật khẩu</h2>
<p style="color: #666;">Xin chào <strong>{{ full_name }}</strong>,</p>
<p style="color: #666;">Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn. Nhấn nút bên dưới để tiếp tục:</p>
<div style="text-align: center; margin: 30px 0;">
  <a href="{{ reset_url }}" style="background: linear-gradient(135deg, #f093fb, #f5576c); color: white; padding: 14px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
    🔑 Đặt lại mật khẩu
  </a>
</div>
<p style="color: #999; font-size: 13px;">Hoặc copy đường link sau vào trình duyệt:<br><code>{{ reset_url }}</code></p>
<p style="color: #999; font-size: 13px;">Link có hiệu lực trong {{ expire_minutes }} phút. Nếu bạn không yêu cầu, hãy bỏ qua email này.</p>
"""


def _get_mail_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
    )


def _render(content_template: str, **kwargs) -> str:
    env = Environment(loader=BaseLoader())
    content_html = env.from_string(content_template).render(**kwargs)
    full_html = env.from_string(BASE_TEMPLATE).render(content=content_html)
    return full_html


async def _send_email(to_email: str, subject: str, html_body: str):
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        print(f"[EMAIL SKIPPED] To: {to_email} | {subject}")
        return

    try:
        msg = MessageSchema(
            subject=f"MedBook – {subject}",
            recipients=[to_email],
            body=html_body,
            subtype=MessageType.html,
        )
        fm = FastMail(_get_mail_config())
        await fm.send_message(msg)
        print(f"[EMAIL SENT] To: {to_email} | {subject}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")


# ── Public API ──

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
    html = _render(
        APPOINTMENT_CONTENT,
        title=title, message=message,
        patient_name=patient_name, doctor_name=doctor_name,
        scheduled_date=scheduled_date, scheduled_time=scheduled_time,
        reason=reason, doctor_notes=doctor_notes,
    )
    await _send_email(to_email, title, html)


async def send_verify_email(to_email: str, full_name: str, token: str):
    verify_url = f"{settings.FRONTEND_URL}/verify-email.html?token={token}"
    
    # Print to console for development testing
    print("\n" + "="*80)
    print(f"✅ [DEVELOPMENT VERIFY LINK] for {full_name} ({to_email}):")
    print(f"👉 {verify_url}")
    print("="*80 + "\n")
    
    html = _render(
        VERIFY_EMAIL_CONTENT,
        full_name=full_name,
        verify_url=verify_url,
        expire_hours=settings.EMAIL_VERIFY_TOKEN_EXPIRE_HOURS,
    )
    await _send_email(to_email, "Xác thực tài khoản", html)


async def send_reset_password_email(to_email: str, full_name: str, token: str):
    reset_url = f"{settings.FRONTEND_URL}/reset-password.html?token={token}"
    
    # Print to console for development testing
    print("\n" + "="*80)
    print(f"🔑 [DEVELOPMENT RESET LINK] for {full_name} ({to_email}):")
    print(f"👉 {reset_url}")
    print("="*80 + "\n")
    
    html = _render(
        RESET_PASSWORD_CONTENT,
        full_name=full_name,
        reset_url=reset_url,
        expire_minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
    )
    await _send_email(to_email, "Đặt lại mật khẩu", html)
