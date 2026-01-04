# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Booking, Room, Category

# -----------------------------
# Расчёт стоимости бронирования
# -----------------------------
def calculate_booking(data: dict) -> dict:
    session: Session = SessionLocal()
    try:
        room = session.query(Room).get(data["room_id"])
        if not room:
            raise ValueError("Комната не найдена")

        category = session.query(Category).get(room.category_id)
        category_name = category.name if category else "не указан"

        base_price = float(room.price_per_night)

        guests = int(data["guests_count"])
        nights = int(data["nights"])
        lunch_count = int(data.get("lunch_count", 0))
        dinner_count = int(data.get("dinner_count", 0))

        total = base_price * nights
        total += lunch_count * 500
        total += dinner_count * 800

        if nights > 3:
            total *= 0.95  # скидка 5%

        return {
            "final_amount": round(total, 2),
            "nights": nights,
            "guests_count": guests,
            "lunch_count": lunch_count,
            "dinner_count": dinner_count,
            "room_category": category_name,
            "base_price_per_night": base_price,
        }
    finally:
        session.close()

# -----------------------------
# Создание бронирования с проверкой занятости
# -----------------------------
def create_booking(data: dict) -> dict:
    session: Session = SessionLocal()
    try:
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

        # Проверка занятости номера
        existing = session.query(Booking).filter(
            Booking.room_id == data["room_id"],
            Booking.start_date < end_date,
            Booking.end_date > start_date,
            Booking.status == "created"  # активные брони
        ).first()

        if existing:
            raise ValueError("Комната занята на выбранные даты.")

        # расчёт суммы
        result = calculate_booking(data)

        booking = Booking(
            room_id=data["room_id"],
            customer_id=data["customer_id"],
            start_date=start_date,
            end_date=end_date,
            final_amount=result["final_amount"],
            status="created"
        )

        session.add(booking)
        session.commit()

        return {
            "booking_id": booking.id,
            "final_amount": result["final_amount"],
            "nights": result["nights"],
            "guests_count": result["guests_count"],
            "lunch_count": result["lunch_count"],
            "dinner_count": result["dinner_count"],
            "room_category": result["room_category"],
            "base_price_per_night": result["base_price_per_night"],
        }
    finally:
        session.close()