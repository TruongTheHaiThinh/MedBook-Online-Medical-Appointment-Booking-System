"""
email.py – Gửi email HTML cho MedBook.
Template đơn giản, không ảnh, gửi nhanh.
"""
from typing import Optional

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from jinja2 import Environment, BaseLoader

from app.config import settings


# ══════════════════════════════════════════════════════════════
#  BASE LAYOUT
# ══════════════════════════════════════════════════════════════
BASE_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>MedBook</title>
</head>
<body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f4f6f9;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" border="0" style="max-width:560px;width:100%;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

          <!-- HEADER -->
          <tr>
            <td style="background:#1a7f74;padding:28px 36px;text-align:center;">
              <p style="margin:0;font-size:22px;font-weight:700;color:#ffffff;letter-spacing:0.5px;">MedBook</p>
              <p style="margin:6px 0 0;font-size:12px;color:rgba(255,255,255,0.8);">Hệ thống Quản lý &amp; Đặt lịch Khám bệnh</p>
            </td>
          </tr>

          <!-- BODY -->
          <tr>
            <td style="padding:32px 36px;">
              {{ content }}
            </td>
          </tr>

          <!-- DIVIDER -->
          <tr>
            <td style="padding:0 36px;">
              <hr style="border:none;border-top:1px solid #e8edf2;margin:0;">
            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td style="padding:20px 36px;text-align:center;">
              <p style="margin:0;font-size:11px;color:#9ca3af;">
                Email này được gửi tự động từ hệ thống MedBook. Vui lòng không trả lời email này.
              </p>
              <p style="margin:6px 0 0;font-size:11px;color:#d1d5db;">
                &copy; 2025 MedBook &bull; medbook.online.vn@gmail.com
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


# ══════════════════════════════════════════════════════════════
#  APPOINTMENT NOTIFICATION
# ══════════════════════════════════════════════════════════════
APPOINTMENT_CONTENT = """
<p style="font-size:18px;font-weight:700;color:#111827;margin:0 0 16px;">{{ title }}</p>
<p style="font-size:14px;color:#374151;margin:0 0 8px;">Xin chào <strong>{{ patient_name }}</strong>,</p>
<p style="font-size:14px;color:#6b7280;margin:0 0 20px;line-height:1.6;">{{ message }}</p>

<table width="100%" cellpadding="12" cellspacing="0" border="0"
  style="background:#f8fafc;border-left:4px solid #1a7f74;border-radius:4px;margin-bottom:16px;">
  <tr>
    <td style="font-size:13px;color:#374151;line-height:1.8;">
      <strong>Bác sĩ:</strong> {{ doctor_name }}<br>
      <strong>Ngày khám:</strong> {{ scheduled_date }}<br>
      <strong>Giờ khám:</strong> {{ scheduled_time }}<br>
      {% if reason %}<strong>Lý do:</strong> {{ reason }}<br>{% endif %}
      {% if doctor_notes %}<strong>Ghi chú:</strong> {{ doctor_notes }}{% endif %}
    </td>
  </tr>
</table>
"""


# ══════════════════════════════════════════════════════════════
#  EMAIL VERIFICATION
# ══════════════════════════════════════════════════════════════
VERIFY_EMAIL_CONTENT = """
<p style="font-size:18px;font-weight:700;color:#111827;margin:0 0 16px;">Xác thực tài khoản</p>
<p style="font-size:14px;color:#374151;margin:0 0 8px;">Xin chào <strong>{{ full_name }}</strong>,</p>
<p style="font-size:14px;color:#6b7280;margin:0 0 24px;line-height:1.6;">
  Cảm ơn bạn đã đăng ký tài khoản <strong>MedBook</strong>!
  Vui lòng nhấn nút bên dưới để xác thực email của bạn:
</p>

<table width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding:8px 0 24px;">
      <a href="{{ verify_url }}"
        style="display:inline-block;background:#1a7f74;color:#ffffff;text-decoration:none;
               padding:14px 40px;border-radius:8px;font-size:14px;font-weight:700;">
        Xác thực Email
      </a>
    </td>
  </tr>
</table>

<div style="background:#f8fafc;border:1px dashed #d1d5db;border-radius:6px;padding:12px 16px;margin-bottom:16px;">
  <p style="font-size:11px;color:#9ca3af;margin:0 0 4px;">Hoặc copy đường link sau vào trình duyệt:</p>
  <p style="font-size:11px;color:#6b7280;word-break:break-all;margin:0;font-family:monospace;">{{ verify_url }}</p>
</div>

<p style="font-size:12px;color:#9ca3af;margin:0;background:#fffbeb;border:1px solid #fde68a;border-radius:6px;padding:10px 14px;">
  Link xác thực có hiệu lực trong <strong>{{ expire_hours }} giờ</strong>.
  Nếu bạn không đăng ký tài khoản này, vui lòng bỏ qua email.
</p>
"""


# ══════════════════════════════════════════════════════════════
#  PASSWORD RESET
# ══════════════════════════════════════════════════════════════
RESET_PASSWORD_CONTENT = """
<p style="font-size:18px;font-weight:700;color:#111827;margin:0 0 16px;">Đặt lại mật khẩu</p>
<p style="font-size:14px;color:#374151;margin:0 0 8px;">Xin chào <strong>{{ full_name }}</strong>,</p>
<p style="font-size:14px;color:#6b7280;margin:0 0 24px;line-height:1.6;">
  Chúng tôi nhận được yêu cầu <strong>đặt lại mật khẩu</strong> cho tài khoản MedBook của bạn.
  Nhấn nút bên dưới để tiếp tục. Yêu cầu này sẽ hết hạn trong
  <strong style="color:#dc2626;">{{ expire_minutes }} phút</strong>.
</p>

<table width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding:8px 0 24px;">
      <a href="{{ reset_url }}"
        style="display:inline-block;background:#dc2626;color:#ffffff;text-decoration:none;
               padding:14px 40px;border-radius:8px;font-size:14px;font-weight:700;">
        Đặt lại mật khẩu
      </a>
    </td>
  </tr>
</table>

<div style="background:#f8fafc;border:1px dashed #d1d5db;border-radius:6px;padding:12px 16px;margin-bottom:16px;">
  <p style="font-size:11px;color:#9ca3af;margin:0 0 4px;">Hoặc copy đường link sau vào trình duyệt:</p>
  <p style="font-size:11px;color:#6b7280;word-break:break-all;margin:0;font-family:monospace;">{{ reset_url }}</p>
</div>

<p style="font-size:12px;color:#9f1239;margin:0;background:#fff1f2;border:1px solid #fecdd3;border-radius:6px;padding:10px 14px;">
  Nếu bạn <em>không</em> yêu cầu đặt lại mật khẩu, hãy bỏ qua email này. Mật khẩu hiện tại của bạn vẫn an toàn.
</p>
"""


# ══════════════════════════════════════════════════════════════
#  Internals
# ══════════════════════════════════════════════════════════════

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
    env = Environment(loader=BaseLoader(), autoescape=False)
    content_html = env.from_string(content_template).render(**kwargs)
    return env.from_string(BASE_TEMPLATE).render(content=content_html)


async def _send_email(to_email: str, subject: str, html_body: str):
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        print(f"[EMAIL SKIPPED] To: {to_email}")
        return
    try:
        msg = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=html_body,
            subtype=MessageType.html,
        )
        fm = FastMail(_get_mail_config())
        await fm.send_message(msg)
        print(f"[EMAIL SENT] To: {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] {type(e).__name__}: {e}")


# ══════════════════════════════════════════════════════════════
#  Public API
# ══════════════════════════════════════════════════════════════

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
    await _send_email(to_email, f"MedBook - {title}", html)


async def send_verify_email(to_email: str, full_name: str, token: str):
    verify_url = f"{settings.FRONTEND_URL}/verify-email.html?token={token}"
    print(f"[VERIFY] {to_email} -> {verify_url}")
    html = _render(
        VERIFY_EMAIL_CONTENT,
        full_name=full_name,
        verify_url=verify_url,
        expire_hours=settings.EMAIL_VERIFY_TOKEN_EXPIRE_HOURS,
    )
    await _send_email(to_email, "MedBook - Xác thực tài khoản", html)


async def send_reset_password_email(to_email: str, full_name: str, token: str):
    reset_url = f"{settings.FRONTEND_URL}/reset-password.html?token={token}"
    print(f"[RESET] {to_email} -> {reset_url}")
    html = _render(
        RESET_PASSWORD_CONTENT,
        full_name=full_name,
        reset_url=reset_url,
        expire_minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
    )
    await _send_email(to_email, "MedBook - Đặt lại mật khẩu", html)
