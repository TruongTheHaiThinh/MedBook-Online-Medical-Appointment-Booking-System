from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, doctors, appointments, admin_hr, admin_cashier, medical_records
from app.config import settings
from app.core.scheduler import start_scheduler
from app.database import get_db
from app.routers.appointments import vnpay_return

app = FastAPI(
    title="MedBook API",
    description="Hệ thống quản lý & đặt lịch khám bệnh trực tuyến – REST API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        settings.FRONTEND_URL,
        settings.FRONTEND_URL.rstrip("/frontend"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(admin_hr.router)
app.include_router(admin_cashier.router)
app.include_router(medical_records.router)



# Duplicate Catcher to handle VNPAY Merchant Portal locked redirects
@app.get("/api/v1/appointments/vnpay-return")
async def vnpay_return_legacy(request: Request, db=Depends(get_db)):
    return await vnpay_return(request, db)


@app.on_event("startup")
async def startup_event():
    start_scheduler()


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.get("/healthz", tags=["Health"])
async def healthz():
    return {"status": "ok"}

