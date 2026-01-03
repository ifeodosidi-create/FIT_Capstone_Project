# app/client_routes.py

from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.booking_service import (
    BookingInput,
    calculate_booking_amount,
    create_booking
)
from app.models import Booking, Payment
from datetime import date

client_bp = Blueprint("client", __name__)


# ---------------------------------------------------------
# 1) Расчёт стоимости бронирования
# ---------------------------------------------------------
@client_bp.route("/booking/calculate", methods=["POST"])
def calculate_booking_route():
    """
    Принимает параметры бронирования и возвращает рассчитанную сумму.
    """

    data = request.get_json()

    try:
        booking_input = BookingInput(
            base_price_per_night=data["base_price_per_night"],
            guests_count=data["guests_count"],
            nights=data["nights"],
            lunch_selected=data["lunch_selected"],
            dinner_selected=data["dinner_selected"],
            is_repeat_within_year=data["is_repeat_within_year"],
        )

        result = calculate_booking_amount(booking_input)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ---------------------------------------------------------
# 2) Создание бронирования
# ---------------------------------------------------------
@client_bp.route("/booking/create", methods=["POST"])
def create_booking_route():
    """
    Создание бронирования в базе данных.
    """

    data = request.get_json()

    try:
        session: Session = SessionLocal()

        booking_input = BookingInput(
            base_price_per_night=data["base_price_per_night"],
            guests_count=data["guests_count"],
            nights=data["nights"],
            lunch_selected=data["lunch_selected"],
            dinner_selected=data["dinner_selected"],
            is_repeat_within_year=data["is_repeat_within_year"],
            start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
            end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date(),
        )

        result = create_booking(
            session=session,
            room_id=data["room_id"],
            customer_id=data["customer_id"],
            data=booking_input
        )

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        session.close()


# ---------------------------------------------------------
# 3) Оплата бронирования
# ---------------------------------------------------------
@client_bp.route("/booking/pay", methods=["POST"])
def pay_booking_route():
    """
    Имитация эквайринга: создаёт Payment и меняет статус брони.
    """

    data = request.get_json()

    try:
        session: Session = SessionLocal()

        booking_id = data["booking_id"]
        method = data["method"]

        booking = session.query(Booking).filter_by(id=booking_id).first()
        if not booking:
            return jsonify({"error": "Бронирование не найдено"}), 404

        # имитация эквайринга
        if data.get("confirm") is not True:
            return jsonify({"message": "Здесь должен быть эквайринг. Подтвердите платеж."})

        payment = Payment(
            booking_id=booking_id,
            amount=booking.final_amount,
            method=method,
            status="success",
            payment_date=date.today()
        )

        booking.status = "paid"

        session.add(payment)
        session.commit()

        return jsonify({
            "booking_id": booking_id,
            "payment_id": payment.id,
            "status": "paid"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        session.close()


# ---------------------------------------------------------
# 4) Отмена бронирования
# ---------------------------------------------------------
@client_bp.route("/booking/cancel", methods=["POST"])
def cancel_booking_route():
    """
    Отмена бронирования.
    Условия:
    - отмена возможна, если до заезда >= 1 день
    - если оплачено → вывести сообщение о возврате по телефону
    """

    data = request.get_json()

    try:
        session: Session = SessionLocal()

        booking_id = data["booking_id"]
        booking = session.query(Booking).filter_by(id=booking_id).first()

        if not booking:
            return jsonify({"error": "Бронирование не найдено"}), 404

        # проверка даты
        today = date.today()
        if booking.start_date <= today:
            return jsonify({"error": "Отмена невозможна: до заезда меньше 1 дня"}), 400

        # если оплачено
        if booking.status == "paid":
            booking.status = "cancelled"
            session.commit()
            return jsonify({
                "booking_id": booking_id,
                "status": "cancelled",
                "message": "За возвратом денежных средств обращайтесь по телефону 880012345678"
            })

        # если не оплачено
        booking.status = "cancelled"
        session.commit()

        return jsonify({
            "booking_id": booking_id,
            "status": "cancelled"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        session.close()