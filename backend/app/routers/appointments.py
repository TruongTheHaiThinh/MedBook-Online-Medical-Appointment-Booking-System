from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func

from app.database import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.user import User
from app.models.specialty import Specialty
from app.models.appointment import Payment
from app.schemas.appointment import (
    AppointmentCreate, AppointmentConfirm, AppointmentCancel,
    AppointmentResponse, AppointmentComplete, AppointmentStatsResponse,
    PaymentResponse,
)
from app.core.security import get_current_user, require_patient, require_doctor, RoleChecker
from app.services.appointment_service import AppointmentService
from app.core.vnpay import VNPay
from app.config import settings

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def _build_response(
    appt: Appointment, 
    patient_name=None,
    patient_phone=None,
    patient_code=None,
    patient_address=None,
    patient_dob=None,
    patient_gender=None,
    patient_blood_type=None,
    doctor_name=None, 
    specialty_name=None,
    queue_number=None,
    room_number=None,
    payment_amount=0,
    payment_status="PENDING"
) -> AppointmentResponse:
    return AppointmentResponse(
        id=appt.id,
        patient_id=appt.patient_id,
        doctor_id=appt.doctor_id,
        scheduled_date=appt.scheduled_date,
        scheduled_time=appt.scheduled_time,
        reason=appt.reason,
        status=appt.status,
        is_revisit=appt.is_revisit,
        qr_code=appt.qr_code,
        doctor_notes=appt.doctor_notes,
        reminder_sent=appt.reminder_sent,
        created_at=appt.created_at,
        patient_name=patient_name,
        patient_phone=patient_phone,
        patient_code=patient_code,
        patient_address=patient_address,
        patient_dob=patient_dob,
        patient_gender=patient_gender,
        patient_blood_type=patient_blood_type,
        doctor_name=doctor_name,
        specialty_name=specialty_name,
        queue_number=queue_number or appt.queue_number,
        room_number=room_number,
        payment_amount=payment_amount,
        payment_status=payment_status
    )


async def _enrich_appointment(appt: Appointment, db: AsyncSession) -> AppointmentResponse:
    """Add patient details, doctor_name, specialty_name to response."""
    # Fetch Patient
    pt_res = await db.execute(select(User).where(User.id == appt.patient_id))
    patient = pt_res.scalar_one_or_none()

    # Fetch Doctor info
    try:
        dr_res = await db.execute(
            select(User.full_name, Specialty.name.label("spec"), Doctor.room_number)
            .join(Doctor, Doctor.user_id == User.id)
            .outerjoin(Specialty, Specialty.id == Doctor.specialty_id)
            .where(Doctor.id == appt.doctor_id)
        )
        dr_data = dr_res.first()
    except Exception:
        dr_data = None

    # Fetch Payment
    p_res = await db.execute(select(Payment).where(Payment.appointment_id == appt.id))
    payment = p_res.scalar_one_or_none()

    return _build_response(
        appt,
        patient_name=patient.full_name if patient else "Bệnh nhân không rõ",
        patient_phone=patient.phone if patient else "---",
        patient_code=patient.patient_code if patient else "MB-XXX",
        patient_address=patient.address if patient else "---",
        patient_dob=patient.date_of_birth.date() if patient and patient.date_of_birth else None,
        patient_gender=patient.gender if patient else "---",
        patient_blood_type=patient.blood_type if patient else "---",
        doctor_name=dr_data[0] if dr_data else "Chưa xác định",
        specialty_name=dr_data[1] if dr_data else "Đa khoa",
        queue_number=appt.queue_number,
        room_number=dr_data[2] if dr_data else "---",
        payment_amount=float(payment.amount) if payment else 0,
        payment_status=payment.status if payment else "PENDING"
    )


# ── Patient endpoints ──

@router.post("", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    data: AppointmentCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_patient),
    db: AsyncSession = Depends(get_db),
):
    """Bệnh nhân đặt lịch hẹn"""
    appt = await AppointmentService.create(
        patient=current_user,
        doctor_id=data.doctor_id,
        scheduled_date=data.scheduled_date,
        scheduled_time=data.scheduled_time,
        reason=data.reason,
        db=db,
        background_tasks=background_tasks,
    )
    return await _enrich_appointment(appt, db)


@router.get("/me", response_model=List[AppointmentResponse])
async def get_my_appointments(
    status: str = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bệnh nhân xem danh sách lịch hẹn của mình"""
    query = select(Appointment).where(Appointment.patient_id == current_user.id)
    if status:
        query = query.where(Appointment.status == status.upper())
    query = query.order_by(Appointment.scheduled_date.desc()).offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    appointments = result.scalars().all()

    responses = []
    for appt in appointments:
        responses.append(await _enrich_appointment(appt, db))
    return responses


@router.patch("/{appointment_id}/pay", response_model=AppointmentResponse)
async def pay_appointment(
    appointment_id: UUID,
    current_user: User = Depends(require_patient),
    db: AsyncSession = Depends(get_db),
):
    """Bệnh nhân thanh toán phí đặt lịch 100k (Simulated - keep for backward compatibility)"""
    appt = await AppointmentService.pay(appointment_id, db, current_user)
    return await _enrich_appointment(appt, db)


@router.get("/{appointment_id}/vnpay-url")
async def get_vnpay_url(
    appointment_id: UUID,
    request: Request,
    bank_code: Optional[str] = Query("NCB"),
    current_user: User = Depends(require_patient),
    db: AsyncSession = Depends(get_db),
):
    """Lấy URL thanh toán VNPAY cho lịch hẹn"""
    appt = await db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")
    if appt.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền thanh toán cho lịch hẹn này")
    if appt.status != "AWAITING_PAYMENT":
        raise HTTPException(status_code=400, detail="Lịch hẹn không ở trạng thái chờ thanh toán")

    vnp = VNPay(settings.VNP_TMN_CODE, settings.VNP_HASH_SECRET, settings.VNP_URL)
    
    # Giả lập IP Address nếu không lấy được từ request (vì đang chạy local)
    ip_addr = "127.0.0.1" 
    
    # Tạo mã giao dịch duy nhất bằng cách đính kèm timestamp để tránh lỗi "Trùng mã giao dịch" trên VNPAY Sandbox
    # Ràng buộc VNPAY: vnp_TxnRef tối đa 30 ký tự. Sử dụng 18 ký tự đầu của UUID + 10 ký tự timestamp = 29 ký tự.
    vnp_TxnRef = f"{str(appt.id)[:18]}_{int(datetime.now().timestamp())}"
    
    order_info = f"Thanh toan dat lich hen {appt.id}"
    vnp_ReturnUrl = "http://127.0.0.1:8000/appointments/vnpay-return"
    vnp_url = vnp.get_payment_url(
        vnp_TxnRef=vnp_TxnRef,
        vnp_Amount=100000, # 100k
        vnp_OrderInfo=order_info,
        vnp_OrderType="medical",
        vnp_ReturnUrl=vnp_ReturnUrl,
        vnp_IpAddr=ip_addr,
        vnp_BankCode=bank_code
    )
    return {"payment_url": vnp_url}


@router.get("/vnpay-return")
async def vnpay_return(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Xử lý kết quả trả về từ VNPAY (Redirect back)"""
    from fastapi.responses import RedirectResponse
    
    query_params = dict(request.query_params)
    vnp = VNPay(settings.VNP_TMN_CODE, settings.VNP_HASH_SECRET, settings.VNP_URL)
    vnp.response_data = query_params.copy()
    
    # Kiểm tra tính hợp lệ của chữ ký
    is_valid = vnp.validate_response(settings.VNP_HASH_SECRET)
    
    vnp_TxnRef = query_params.get("vnp_TxnRef")
    vnp_ResponseCode = query_params.get("vnp_ResponseCode")
    
    appt_id_str = vnp_TxnRef.split("_")[0] if vnp_TxnRef and "_" in vnp_TxnRef else vnp_TxnRef
    success = (vnp_ResponseCode == "00")
    if is_valid and success:
        # Thanh toán thành công -> Cập nhật trạng thái lịch hẹn bằng prefix like
        from sqlalchemy import cast, String as SAString
        stmt = select(Appointment).where(cast(Appointment.id, SAString).like(f"{appt_id_str}%"))
        res = await db.execute(stmt)
        appt = res.scalar_one_or_none()
        if appt:
            # Tránh xử lý lại nếu IPN chạy trước
            if appt.status == "AWAITING_PAYMENT":
                pt_res = await db.execute(select(User).where(User.id == appt.patient_id))
                patient = pt_res.scalar_one_or_none()
                if patient:
                    await AppointmentService.pay(appt.id, db, patient)
        
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/patient/dashboard.html?payment=success")
    else:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/patient/dashboard.html?payment=failed")


@router.get("/vnpay-ipn")
async def vnpay_ipn(
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Xử lý giao dịch ngầm (IPN) từ VNPAY để cập nhật cơ sở dữ liệu đáng tin cậy"""
    query_params = dict(request.query_params)
    
    if not query_params:
        return {"RspCode": "99", "Message": "Invalid request"}
        
    vnp = VNPay(settings.VNP_TMN_CODE, settings.VNP_HASH_SECRET, settings.VNP_URL)
    vnp.response_data = query_params.copy()
    
    # 1. Xác thực chữ ký số
    is_valid = vnp.validate_response(settings.VNP_HASH_SECRET)
    if not is_valid:
        print("[VNPAY IPN ERROR] Sai chữ ký checksum")
        return {"RspCode": "97", "Message": "Invalid Signature"}
        
    vnp_TxnRef = query_params.get("vnp_TxnRef")
    vnp_ResponseCode = query_params.get("vnp_ResponseCode")
    vnp_Amount = query_params.get("vnp_Amount")
    
    appt_id_str = vnp_TxnRef.split("_")[0] if "_" in vnp_TxnRef else vnp_TxnRef
        
    # 2. Tìm kiếm lịch hẹn trong DB bằng prefix like
    from sqlalchemy import cast, String as SAString
    stmt = select(Appointment).where(cast(Appointment.id, SAString).like(f"{appt_id_str}%"))
    res = await db.execute(stmt)
    appt = res.scalar_one_or_none()
    if not appt:
        return {"RspCode": "01", "Message": "Order not found"}
        
    # 3. Kiểm tra số tiền (VNPAY Amount nhân 100, phí đặt lịch là 100,000 VNĐ)
    expected_amount = 100000 * 100 
    try:
        vnp_amount_val = int(vnp_Amount)
    except ValueError:
        return {"RspCode": "04", "Message": "Invalid Amount"}
        
    if vnp_amount_val != expected_amount:
        print(f"[VNPAY IPN ERROR] Sai số tiền: Nhận {vnp_amount_val}, mong đợi {expected_amount}")
        return {"RspCode": "04", "Message": "Invalid Amount"}
        
    # 4. Kiểm tra xem lịch hẹn đã được thanh toán trước đó chưa
    if appt.status != "AWAITING_PAYMENT":
        p_res = await db.execute(select(Payment).where(Payment.appointment_id == appt.id))
        payment = p_res.scalar_one_or_none()
        if payment and payment.status == "PAID":
            return {"RspCode": "02", "Message": "Order already confirmed"}
            
    # 5. Xử lý cập nhật trạng thái nếu giao dịch thành công (ResponseCode == "00")
    if vnp_ResponseCode == "00":
        pt_res = await db.execute(select(User).where(User.id == appt.patient_id))
        patient = pt_res.scalar_one_or_none()
        if patient:
            await AppointmentService.pay(appt.id, db, patient)
            print(f"[VNPAY IPN SUCCESS] Cập nhật thành công lịch hẹn {appt.id}")
            return {"RspCode": "00", "Message": "Confirm Success"}
        else:
            return {"RspCode": "01", "Message": "Patient not found"}
    else:
        print(f"[VNPAY IPN] Giao dịch không thành công với mã lỗi {vnp_ResponseCode}")
        return {"RspCode": "00", "Message": "Transaction failed recorded"}


@router.get("/qr/{qr_code}", response_model=AppointmentResponse)
async def get_appointment_by_qr(
    qr_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user), 
):
    """Tìm lịch hẹn theo mã QR"""
    from sqlalchemy import cast, String as SAString
    code = qr_code.strip()
    # Tìm kiếm linh hoạt: khớp hoàn toàn qr_code, hoặc khớp một phần qr_code/ID
    stmt = select(Appointment).where(
        or_(
            Appointment.qr_code == code,
            Appointment.qr_code.ilike(f"%{code}%"),
            cast(Appointment.id, SAString).ilike(f"%{code}%")
        )
    )
    result = await db.execute(stmt)
    appointment = result.scalars().first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail=f"Tra cứu: Không tìm thấy mã {qr_code}")
    
    return await _enrich_appointment(appointment, db)


# ── Doctor endpoints ──

@router.get("/doctor/list", response_model=List[AppointmentResponse])
async def get_doctor_appointments(
    status: str = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Bác sĩ xem danh sách lịch hẹn"""
    result = await db.execute(select(Doctor).where(Doctor.user_id == current_user.id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bác sĩ")

    query = select(Appointment).where(Appointment.doctor_id == doctor.id)
    if status:
        query = query.where(Appointment.status == status.upper())
    query = query.order_by(Appointment.scheduled_date.asc()).offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    appointments = result.scalars().all()

    responses = []
    for appt in appointments:
        responses.append(await _enrich_appointment(appt, db))
    return responses


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment_detail(
    appointment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lấy chi tiết một lịch hẹn (dùng cho bác sĩ khám bệnh)"""
    appt = await db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")
    return await _enrich_appointment(appt, db)


# ── State transitions ──

@router.patch("/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(
    appointment_id: UUID,
    data: AppointmentConfirm,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(RoleChecker(["cashier_admin", "hr_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Thu ngân xác nhận: PENDING → CONFIRMED"""
    appt = await AppointmentService.transition(
        appointment_id, "CONFIRMED", db, current_user, data.doctor_notes, background_tasks,
    )
    return await _enrich_appointment(appt, db)


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: UUID,
    data: AppointmentCancel,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Hủy lịch hẹn (bệnh nhân trước 24h, thu ngân/bác sĩ không giới hạn)"""
    appt = await AppointmentService.transition(
        appointment_id, "CANCELLED", db, current_user, data.doctor_notes, background_tasks,
    )
    return await _enrich_appointment(appt, db)


@router.patch("/{appointment_id}/checkin", response_model=AppointmentResponse)
async def checkin_appointment(
    appointment_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(RoleChecker(["cashier_admin", "hr_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Thu ngân check-in: CONFIRMED → IN_PROGRESS"""
    appt = await AppointmentService.transition(
        appointment_id, "IN_PROGRESS", db, current_user, background_tasks=background_tasks,
    )
    return await _enrich_appointment(appt, db)


@router.post("/checkin-qr", response_model=AppointmentResponse)
async def checkin_by_qr(
    qr_code: str = Query(..., description="Mã QR của lịch hẹn"),
    current_user: User = Depends(RoleChecker(["cashier_admin", "hr_admin", "cashier"])),
    db: AsyncSession = Depends(get_db),
):
    """Thu ngân quét QR check-in bệnh nhân"""
    appt = await AppointmentService.checkin_by_qr(qr_code, db, current_user)
    if not appt:
        raise HTTPException(status_code=404, detail=f"Không thể check-in: Lịch hẹn với mã {qr_code} không hợp lệ hoặc không tìm thấy")
    return await _enrich_appointment(appt, db)


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
async def complete_appointment(
    appointment_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(RoleChecker(["cashier_admin", "hr_admin", "cashier"])),
    db: AsyncSession = Depends(get_db),
):
    """Thu ngân hoàn thành: PRESCRIPTION_SENT → COMPLETED"""
    appt = await AppointmentService.transition(
        appointment_id, "COMPLETED", db, current_user, background_tasks=background_tasks,
    )
    return await _enrich_appointment(appt, db)


# ── All appointments (for cashier dashboard) ──

# ── Cashier Specialized Optimized Endpoints ──

@router.get("/cashier/stats", response_model=AppointmentStatsResponse)
async def get_cashier_stats(
    current_user: User = Depends(RoleChecker(["cashier_admin", "hr_admin", "cashier"])),
    db: AsyncSession = Depends(get_db),
):
    """Lấy số liệu thống kê nhanh cho Dashboard Thu ngân"""
    from datetime import date
    today = date.today()
    
    # Query all today's appointments
    res_today = await db.execute(select(Appointment).where(Appointment.scheduled_date == today))
    today_appts = res_today.scalars().all()
    
    # Biến tính toán dựa trên ngày
    total_today = len(today_appts)
    completed_today = len([a for a in today_appts if a.status == "COMPLETED"])
    
    # Biến tính toán toàn cục (Global counts to never miss any workload)
    res_all_pending = await db.execute(select(Appointment).where(Appointment.status.in_(["PENDING", "AWAITING_PAYMENT"])))
    total_pending = len(res_all_pending.scalars().all())
    
    # Số ca chờ thanh toán ban đầu (AWAITING_PAYMENT) - có thể hiển thị nếu muốn
    res_awaiting_pay = await db.execute(select(Appointment).where(Appointment.status == "AWAITING_PAYMENT"))
    total_awaiting_pay = len(res_awaiting_pay.scalars().all())
    
    # Số ca "Chờ khám" (Đã duyệt nhưng chưa check-in) + "Đang khám" (Đã quét QR) toàn cục
    res_in_progress = await db.execute(select(Appointment).where(Appointment.status.in_(["CONFIRMED", "IN_PROGRESS"])))
    total_in_exam = len(res_in_progress.scalars().all())
    
    res_all_waiting_pay = await db.execute(select(Appointment).where(Appointment.status == "PRESCRIPTION_SENT"))
    total_waiting_pay = len(res_all_waiting_pay.scalars().all())

    revenue_today = completed_today * 150000.0
    s_rate = (completed_today / total_today * 100) if total_today > 0 else 0
    
    return AppointmentStatsResponse(
        total_today=total_today,
        pending_approval=total_pending,
        waiting_checkin=total_in_exam,
        waiting_payment=total_waiting_pay,
        completed_today=completed_today,
        revenue_today=revenue_today,
        success_rate=round(s_rate, 1),
        cancel_rate=0.0
    )

@router.get("/cashier/reception", response_model=List[AppointmentResponse])
async def get_reception_queue(
    current_user: User = Depends(RoleChecker(["cashier_admin", "hr_admin", "cashier"])),
    db: AsyncSession = Depends(get_db),
):
    """Danh sách chờ duyệt & check-in (Optimized)"""
    from datetime import date
    from sqlalchemy import or_
    
    # Hiển thị:
    # 1. TẤT CẢ các ca PENDING hoặc AWAITING_PAYMENT (dù ngày nào cũng phải duyệt/theo dõi)
    # 2. Các ca CONFIRMED hoặc IN_PROGRESS (Thường là cho hôm nay, nhưng hiện tất cả CONFIRMED để Thu ngân dễ check-in)
    query = select(Appointment).where(
        or_(
            Appointment.status.in_(["PENDING", "AWAITING_PAYMENT", "CONFIRMED"]),
            (Appointment.status == "IN_PROGRESS") # Đang khám thì hiện ca hôm nay thôi? Không, hiện hết để quản lý
        )
    ).order_by(Appointment.status.desc(), Appointment.created_at.asc())
    
    result = await db.execute(query)
    appointments = result.scalars().all()
    return [await _enrich_appointment(a, db) for a in appointments]

@router.get("/cashier/history", response_model=List[AppointmentResponse])
async def get_cashier_history(
    current_user: User = Depends(RoleChecker(["cashier_admin", "hr_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Danh sách TẤT CẢ các ca khám để Thu ngân tra cứu lịch sử"""
    query = select(Appointment).order_by(Appointment.created_at.desc()).limit(100) # Giới hạn 100 ca gần nhất
    result = await db.execute(query)
    appointments = result.scalars().all()
    return [await _enrich_appointment(a, db) for a in appointments]

@router.get("/cashier/finance", response_model=List[AppointmentResponse])
async def get_finance_queue(
    current_user: User = Depends(RoleChecker(["cashier_admin", "hr_admin", "cashier"])),
    db: AsyncSession = Depends(get_db),
):
    """Danh sách chờ thanh toán (Optimized)"""
    from datetime import date
    query = select(Appointment).where(
        Appointment.status == "PRESCRIPTION_SENT"
    ).order_by(Appointment.created_at.asc())
    
    result = await db.execute(query)
    appointments = result.scalars().all()
    return [await _enrich_appointment(a, db) for a in appointments]


@router.get("/all", response_model=List[AppointmentResponse])
async def get_all_appointments(
    status: str = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(RoleChecker(["cashier_admin", "hr_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Thu ngân / HR Admin xem toàn bộ lịch hẹn"""
    query = select(Appointment)
    if status:
        query = query.where(Appointment.status == status.upper())
    query = query.order_by(Appointment.scheduled_date.desc()).offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    appointments = result.scalars().all()

    responses = []
    for appt in appointments:
        responses.append(await _enrich_appointment(appt, db))
    return responses


@router.patch("/{appointment_id}/complete-exam", response_model=AppointmentResponse)
async def complete_examination(
    appointment_id: UUID,
    data: AppointmentComplete,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db),
):
    """Bác sĩ hoàn tất khám và gửi đơn thuốc: IN_PROGRESS -> PRESCRIPTION_SENT"""
    appt = await AppointmentService.transition(
        appointment_id, "PRESCRIPTION_SENT", db, current_user, data.doctor_notes, background_tasks
    )
    return await _enrich_appointment(appt, db)

