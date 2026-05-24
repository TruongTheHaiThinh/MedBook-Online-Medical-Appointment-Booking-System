# ── DEPRECATED ──
# PrescriptionItem model has been moved to app/models/appointment.py
# This file is kept for backward compatibility with existing imports.
from app.models.appointment import PrescriptionItem

__all__ = ["PrescriptionItem"]
