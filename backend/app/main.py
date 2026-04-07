from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, doctors, specialties, schedules, appointments, admin
from app.tasks.reminder_task import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle hooks."""
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## 🏥 MedBook – Patient Appointment Booking System API

Hệ thống đặt lịch khám bệnh trực tuyến dành cho phòng khám tư nhân và trạm y tế.

### Vai trò người dùng
- **Patient** – tìm kiếm bác sĩ và đặt lịch khám
- **Doctor** – quản lý lịch làm việc và xác nhận ca khám  
- **Admin** – giám sát toàn hệ thống và phê duyệt tài khoản

### Luồng nghiệp vụ chính
1. Patient đăng ký → Đặt lịch → Nhận email xác nhận (PENDING)
2. Doctor xác nhận → Patient nhận email (CONFIRMED) → Nhắc lịch 24h trước
3. Doctor hoàn thành ca khám → COMPLETED
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS – allow all origins for development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers
app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(specialties.router)
app.include_router(schedules.router)
app.include_router(appointments.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
