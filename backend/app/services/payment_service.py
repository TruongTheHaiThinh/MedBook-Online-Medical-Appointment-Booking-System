"""
PaymentService – Cashier payment processing and revenue tracking.
"""
from datetime import datetime, date, timedelta
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.appointment import Appointment, Payment
from app.models.user import User


class PaymentService:

    @staticmethod
    async def create_payment(
        appointment_id: UUID,
        amount: float,
        payment_method: str,
        cashier: User,
        db: AsyncSession,
    ) -> Payment:
        """Cashier creates payment for PRESCRIPTION_SENT appointment -> COMPLETED."""
        # Verify appointment
        result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
        appointment = result.scalar_one_or_none()
        if not appointment:
            raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")

        if appointment.status != "PRESCRIPTION_SENT":
            raise HTTPException(
                status_code=400,
                detail=f"Chỉ có thể thu phí cho lịch hẹn PRESCRIPTION_SENT, hiện tại: {appointment.status}",
            )

        # Check if payment already exists
        existing = await db.execute(select(Payment).where(Payment.appointment_id == appointment_id))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Lịch hẹn này đã được thanh toán")

        payment = Payment(
            appointment_id=appointment_id,
            cashier_id=cashier.id,
            amount=amount,
            payment_method=payment_method,
            status="PAID",
            paid_at=datetime.utcnow(),
        )
        db.add(payment)

        # Transition to COMPLETED
        appointment.status = "COMPLETED"

        await db.commit()
        await db.refresh(payment)
        return payment

    @staticmethod
    async def get_by_appointment(appointment_id: UUID, db: AsyncSession) -> Payment:
        result = await db.execute(select(Payment).where(Payment.appointment_id == appointment_id))
        payment = result.scalar_one_or_none()
        if not payment:
            raise HTTPException(status_code=404, detail="Không tìm thấy thông tin thanh toán")
        return payment

    @staticmethod
    async def get_revenue_summary(
        db: AsyncSession,
        days: int = 30,
    ) -> dict:
        """Revenue summary for cashier dashboard."""
        start_date = date.today() - timedelta(days=days)

        # Total revenue
        total_result = await db.execute(
            select(func.sum(Payment.amount)).where(Payment.status == "PAID")
        )
        total_revenue = total_result.scalar() or 0

        # Revenue in period
        period_result = await db.execute(
            select(func.sum(Payment.amount)).where(
                Payment.status == "PAID",
                Payment.paid_at >= datetime.combine(start_date, datetime.min.time()),
            )
        )
        period_revenue = period_result.scalar() or 0

        # Daily breakdown
        daily_result = await db.execute(
            select(
                func.date_trunc("day", Payment.paid_at).label("day"),
                func.sum(Payment.amount).label("total"),
                func.count(Payment.id).label("count"),
            )
            .where(
                Payment.status == "PAID",
                Payment.paid_at >= datetime.combine(start_date, datetime.min.time()),
            )
            .group_by(func.date_trunc("day", Payment.paid_at))
            .order_by(func.date_trunc("day", Payment.paid_at).asc())
        )
        daily_data = daily_result.all()

        return {
            "total_revenue": float(total_revenue),
            "period_revenue": float(period_revenue),
            "period_days": days,
            "daily_breakdown": [
                {"date": str(row.day.date()) if row.day else None, "total": float(row.total), "count": row.count}
                for row in daily_data
            ],
        }
