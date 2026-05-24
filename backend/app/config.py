from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ── Database (PostgreSQL) ──
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/medbook"

    # ── JWT ──
    SECRET_KEY: str = "medbook-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Email Verification & Password Reset ──
    EMAIL_VERIFY_TOKEN_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15

    # ── SMTP (Gmail) ──
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # ── App ──
    APP_NAME: str = "MedBook"
    FRONTEND_URL: str = "http://localhost:5500"

    # ── VNPAY ──
    VNP_TMN_CODE: str = "2QXG2Y47"
    VNP_HASH_SECRET: str = ""
    VNP_URL: str = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    VNP_RETURN_URL: str = "http://127.0.0.1:8000/appointments/vnpay-return"

    def __init__(self, **values):
        super().__init__(**values)
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        elif self.DATABASE_URL.startswith("postgresql://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
