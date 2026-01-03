# app/services/booking_service.py
from dataclasses import dataclass
from datetime import date
from typing import Optional

LUNCH_PRICE = 600
DINNER_PRICE = 800

@dataclass
class BookingInput:
    base_price_per_night: int
    guests_count: int
    nights: int
    lunch_selected: bool
    dinner_selected: bool
    is_repeat_within_year: bool
    start_date: Optional[date] = None
    end_date: Optional[date] = None

def calculate_booking_amount(data: BookingInput) -> dict:
    if data.guests_count <= 0 or data.nights <= 0 or data.base_price_per_night <= 0:
        raise ValueError("Некорректные входные данные для расчёта.")

    base_total = data.base_price_per_night * data.nights

    meals_total = 0
    if data.lunch_selected:
        meals_total += LUNCH_PRICE * data.guests_count * data.nights
    if data.dinner_selected:
        meals_total += DINNER_PRICE * data.guests_count * data.nights

    discount_repeat = 5.0 if data.is_repeat_within_year else 0.0
    discount_nights = 5.0 if data.nights >= 3 else 0.0
    discount_sum_percent = discount_repeat + discount_nights

    subtotal = base_total + meals_total
    final_amount = round(subtotal * (1 - discount_sum_percent / 100))

    return {
        "base_total": base_total,
        "meals_total": meals_total,
        "discount_repeat": discount_repeat,
        "discount_nights": discount_nights,
        "discount_sum_percent": discount_sum_percent,
        "final_amount": final_amount,
    }