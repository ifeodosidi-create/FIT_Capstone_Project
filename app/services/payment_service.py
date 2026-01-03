# app/services/payment_service.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PaymentInput:
    booking_id: int
    amount: int
    method: str  # например: "card", "cash"

def create_payment(data: PaymentInput) -> dict:
    """
    Создаёт транзакцию типа 'income' при оплате брони.
    Возвращает словарь с деталями платежа.
    """
    if data.amount <= 0:
        raise ValueError("Сумма должна быть больше 0")

    transaction = {
        "booking_id": data.booking_id,
        "amount": data.amount,
        "method": data.method,
        "type": "income",
        "timestamp": datetime.now().isoformat()
    }
    return transaction