from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, doctors, appointments, admin, prescriptions
from app.config import settings
from app.core.scheduler import start_scheduler

app = FastAPI(
    title="MedBook API",
    description="Hệ thống đặt lịch khám bệnh trực tuyến – REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(admin.router)
app.include_router(prescriptions.router)


@app.on_event("startup")
async def startup_event():
    start_scheduler()


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
