from datetime import datetime
from app.db import SessionLocal
from app.models import Booking, Customer, Room

def calculate_booking(data):
    """
    Расчёт стоимости брони без скидки за повторный заезд.
    """
    start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(data["end_date"], "%Y-%m-%d")
    nights = (end_date - start_date).days

    base_price = float(data["base_price_per_night"])
    guests = int(data["guests_count"])
    lunch_count = int(data.get("lunch_count", 0))
    dinner_count = int(data.get("dinner_count", 0))

    # Стоимость проживания
    amount = nights * base_price

    # Питание
    amount += lunch_count * 500
    amount += dinner_count * 700

    return {
        "nights": nights,
        "base_price_per_night": base_price,
        "guests_count": guests,
        "lunch_count": lunch_count,
        "dinner_count": dinner_count,
        "final_amount": amount,
    }

def create_booking(data):
    """
    Создание брони в БД.
    """
    session = SessionLocal()
    result = calculate_booking(data)

    # Новый клиент
    if data["customer_id"] == "new":
        customer = Customer(
            full_name=data["full_name"],
            phone=data["phone"],
            email=data["email"]
        )
        session.add(customer)
        session.commit()
        customer_id = customer.id
    else:
        customer_id = int(data["customer_id"])

    booking = Booking(
        customer_id=customer_id,
        room_id=int(data["room_id"]),
        start_date=datetime.strptime(data["start_date"], "%Y-%m-%d"),
        end_date=datetime.strptime(data["end_date"], "%Y-%m-%d"),
        guests_count=int(data["guests_count"]),
        base_price_per_night=float(data["base_price_per_night"]),
        lunch_count=int(data.get("lunch_count", 0)),
        dinner_count=int(data.get("dinner_count", 0)),
        final_amount=result["final_amount"],
        status="created"
    )
    session.add(booking)
    session.commit()

    result["booking_id"] = booking.id
    result["status"] = booking.status
    return result