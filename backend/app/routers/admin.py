# ── DEPRECATED ──
# Admin router has been split into admin_hr.py and admin_cashier.py
# This file is kept for backward compatibility.
# Import routers from new locations:
from app.routers.admin_hr import router as hr_router
from app.routers.admin_cashier import router as cashier_router
