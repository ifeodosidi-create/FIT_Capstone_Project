from flask import Blueprint, jsonify, request
from datetime import datetime

from app.services.booking_service import BookingInput, calculate_booking_amount
from app.services.payment_service import PaymentInput, create_payment
from app.services.cancellation_service import CancellationInput, cancel_booking

client_bp = Blueprint("client", __name__)

# -----------------------------
# Список номеров (заглушка)
# -----------------------------
@client_bp.route("/rooms", methods=["GET"])
def get_rooms():
    return jsonify({"message": "Список номеров (заглушка)"})


# -----------------------------
# Расчёт стоимости брони
# -----------------------------
@client_bp.route("/booking/calculate", methods=["POST"])
def booking_calculate():
    payload = request.get_json(force=True)

    data = BookingInput(
        base_price_per_night=int(payload.get("base_price_per_night", 0)),
        guests_count=int(payload.get("guests_count", 1)),
        nights=int(payload.get("nights", 1)),
        lunch_selected=bool(payload.get("lunch_selected", False)),
        dinner_selected=bool(payload.get("dinner_selected", False)),
        is_repeat_within_year=bool(payload.get("is_repeat_within_year", False)),
    )

    try:
        res = calculate_booking_amount(data)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# -----------------------------
# Оплата брони
# -----------------------------
@client_bp.route("/booking/pay", methods=["POST"])
def booking_pay():
    payload = request.get_json(force=True)
    data = PaymentInput(
        booking_id=int(payload.get("booking_id", 0)),
        amount=int(payload.get("amount", 0)),
        method=payload.get("method", "card")
    )
    try:
        res = create_payment(data)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# -----------------------------
# Отмена брони
# -----------------------------
@client_bp.route("/booking/cancel", methods=["POST"])
def booking_cancel():
    payload = request.get_json(force=True)
    data = CancellationInput(
        booking_id=int(payload.get("booking_id", 0)),
        paid=bool(payload.get("paid", False)),
        start_date=datetime.fromisoformat(payload.get("start_date"))
    )
    res = cancel_booking(data)
    return jsonify(res)