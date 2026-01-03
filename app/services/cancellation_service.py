# app/services/cancellation_service.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CancellationInput:
    booking_id: int
    paid: bool
    start_date: datetime

def cancel_booking(data: CancellationInput) -> dict:
    """
    Логика отмены брони:
    - Если бронь оплачена и до заезда < 1 суток → возврат не делаем.
    - Если бронь оплачена и до заезда >= 1 суток → возврат возможен.
    - Если бронь не оплачена → просто отменяем.
    """
    now = datetime.now()
    hours_to_start = (data.start_date - now).total_seconds() / 3600

    if data.paid:
        if hours_to_start < 24:
            return {
                "booking_id": data.booking_id,
                "status": "cancelled",
                "refund": False,
                "message": "Отмена менее чем за сутки — возврат невозможен."
            }
        else:
            return {
                "booking_id": data.booking_id,
                "status": "cancelled",
                "refund": True,
                "message": "Бронь отменена, возврат средств возможен."
            }
    else:
        return {
            "booking_id": data.booking_id,
            "status": "cancelled",
            "refund": False,
            "message": "Бронь отменена (не была оплачена)."
        }