from app.schemas.user import UserRegister, UserLogin, UserResponse, UserUpdate, TokenResponse
from app.schemas.doctor import SpecialtyCreate, SpecialtyUpdate, SpecialtyResponse, DoctorProfileResponse, DoctorProfileUpdate
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, AvailableSlotsResponse
from app.schemas.appointment import AppointmentCreate, AppointmentConfirm, AppointmentCancel, AppointmentResponse

__all__ = [
    "UserRegister", "UserLogin", "UserResponse", "UserUpdate", "TokenResponse",
    "SpecialtyCreate", "SpecialtyUpdate", "SpecialtyResponse", "DoctorProfileResponse", "DoctorProfileUpdate",
    "ScheduleCreate", "ScheduleResponse", "AvailableSlotsResponse",
    "AppointmentCreate", "AppointmentConfirm", "AppointmentCancel", "AppointmentResponse",
]
