import random
from datetime import datetime, timedelta
from faker import Faker

from app.db import SessionLocal
from app.models import Category, Room, Customer, Booking, Payment, Transaction

fake = Faker("ru_RU")
db = SessionLocal()

# -----------------------------
# 1. Создание категорий номеров
# -----------------------------
def seed_categories():
    categories = [
        ("Стандарт", "Базовый номер для 1–2 гостей", 3500),
        ("Комфорт", "Улучшенный номер с рабочей зоной", 4500),
        ("Семейный", "Большой номер для семьи", 6000),
        ("Люкс", "Просторный номер с гостиной", 9000),
        ("Премиум Люкс", "VIP номер с панорамным видом", 15000),
    ]

    for name, desc, price in categories:
        db.add(Category(name=name, description=desc, base_price=price))

    db.commit()
    print("Категории созданы.")


# -----------------------------
# 2. Создание 50 номеров
# -----------------------------
def seed_rooms():
    categories = db.query(Category).all()

    for i in range(1, 51):
        category = random.choice(categories)
        room = Room(
            number=i,
            category_id=category.id,
            capacity=random.choice([1, 2, 3, 4]),
            price_per_night=category.base_price + random.randint(0, 2000)
        )
        db.add(room)

    db.commit()
    print("50 номеров созданы.")


# -----------------------------
# 3. Создание 80 клиентов
# -----------------------------
def seed_customers():
    for _ in range(80):
        customer = Customer(
            full_name=fake.name(),
            phone=fake.phone_number(),
            email=fake.email()
        )
        db.add(customer)

    db.commit()
    print("80 клиентов созданы.")


# -----------------------------
# 4. Создание 100 бронирований
# -----------------------------
def seed_bookings():
    rooms = db.query(Room).all()
    customers = db.query(Customer).all()

    BREAKFAST_PRICE = 300
    LUNCH_PRICE = 600
    DINNER_PRICE = 800

    for _ in range(100):
        room = random.choice(rooms)
        customer = random.choice(customers)

        start_date = fake.date_between(start_date="-6M", end_date="today")
        end_date = start_date + timedelta(days=random.randint(1, 14))
        nights = (end_date - start_date).days
        guests = random.randint(1, room.capacity)

        # питание
        breakfast_count = guests * nights
        lunch_count = (guests * nights) if random.choice([True, False]) else 0
        dinner_count = (guests * nights) if random.choice([True, False]) else 0

        # расчёт стоимости
        base_amount = nights * room.price_per_night
        meals_total = breakfast_count * BREAKFAST_PRICE + lunch_count * LUNCH_PRICE + dinner_count * DINNER_PRICE
        final_amount = base_amount + meals_total

        booking = Booking(
            room_id=room.id,
            customer_id=customer.id,
            start_date=start_date,
            end_date=end_date,
            total_amount=base_amount,
            status=random.choice(["confirmed", "completed", "cancelled"]),
            guests_count=guests,
            breakfast_count=breakfast_count,
            lunch_count=lunch_count,
            dinner_count=dinner_count,
            discount_nights=0.0,
            discount_repeat=0.0,
            final_amount=final_amount
        )
        db.add(booking)

    db.commit()
    print("100 бронирований созданы.")


# -----------------------------
# 5. Создание платежей и транзакций
# -----------------------------
def seed_payments_and_transactions():
    bookings = db.query(Booking).all()

    for booking in bookings:
        if booking.status == "cancelled":
            continue

        amount = booking.final_amount
        payment = Payment(
            booking_id=booking.id,
            amount=amount,
            payment_date=booking.start_date,
            method=random.choice(["cash", "card", "online", "bank"])
        )
        db.add(payment)
        db.commit()

        transaction = Transaction(
            payment_id=payment.id,
            amount=amount,
            transaction_date=payment.payment_date,
            type="income"
        )
        db.add(transaction)

    db.commit()
    print("Платежи и транзакции созданы.")


# -----------------------------
# Запуск всех функций
# -----------------------------
if __name__ == "__main__":
    seed_categories()
    seed_rooms()
    seed_customers()
    seed_bookings()
    seed_payments_and_transactions()

    print("\nГотово! База данных заполнена тестовыми данными.")