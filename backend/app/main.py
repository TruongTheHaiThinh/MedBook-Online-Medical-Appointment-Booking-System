from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, doctors, appointments, admin_hr, admin_cashier, medical_records, news
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
        "https://medbook-medical.vercel.app",
        settings.FRONTEND_URL.rstrip("/"),
        settings.FRONTEND_URL.rstrip("/").rstrip("/frontend"),
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
app.include_router(news.router)



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


@app.get("/debug-db", tags=["Health"])
async def debug_db():
    """Temporary debug: show what DATABASE_URL is being used"""
    from app.database import _db_url, _connect_args
    return {
        "db_url_masked": _db_url.split("@")[1] if "@" in _db_url else _db_url,
        "db_url_scheme": _db_url.split("://")[0] if "://" in _db_url else "unknown",
        "ssl_in_url": "ssl" in _db_url.lower(),
        "connect_args_keys": list(_connect_args.keys()),
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    from fastapi.responses import JSONResponse
    import traceback
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "traceback": traceback.format_exc(),
        }
    )

