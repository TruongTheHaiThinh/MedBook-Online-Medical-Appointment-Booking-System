from app.routers.auth import router as auth_router
from app.routers.doctors import router as doctors_router
from app.routers.appointments import router as appointments_router
from app.routers.admin_hr import router as admin_hr_router
from app.routers.admin_cashier import router as admin_cashier_router
from app.routers.medical_records import router as medical_records_router

__all__ = [
    "auth_router", "doctors_router", "appointments_router",
    "admin_hr_router", "admin_cashier_router", "medical_records_router",
]
