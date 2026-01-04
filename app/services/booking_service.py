from datetime import datetime
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Booking


# -----------------------------
# Расчёт стоимости бронирования
# -----------------------------
def calculate_booking(data: dict) -> dict:
    """
    Рассчитывает итоговую стоимость бронирования.
    Ожидает словарь с ключами:
    - base_price_per_night
    - guests_count
    - nights
    - lunch_count
    - dinner_count
    """
    base_price = float(data["base_price_per_night"])
    guests = int(data["guests_count"])
    nights = int(data["nights"])
    lunch_count = int(data.get("lunch_count", 0))
    dinner_count = int(data.get("dinner_count", 0))

    # Стоимость проживания
    total = base_price * nights

    # Питание (фиксированные цены)
    total += lunch_count * 500
    total += dinner_count * 800

    return {
        "final_amount": total,
        "nights": nights,
        "guests_count": guests,
        "lunch_count": lunch_count,
        "dinner_count": dinner_count,
    }


# -----------------------------
# Создание бронирования
# -----------------------------
def create_booking(data: dict) -> dict:
    """
    Создаёт запись Booking в базе.
    Ожидает словарь с ключами:
    - base_price_per_night, guests_count, nights, lunch_count, dinner_count
    - start_date, end_date, customer_id, room_id
    """
    session: Session = SessionLocal()
    try:
        # расчёт суммы
        result = calculate_booking(data)

        booking = Booking(
            room_id=data["room_id"],
            customer_id=data["customer_id"],
            start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
            end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date(),
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
        }
    finally:
        session.close()