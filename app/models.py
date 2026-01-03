"""
SQLAlchemy модели для системы бронирования.
Содержат сущности: категории, номера, клиенты, бронирования, платежи, транзакции.
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.db import Base


# -----------------------------
# CATEGORY
# -----------------------------
class Category(Base):
    """
    Категория номера: название, описание, базовая цена.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    base_price = Column(Integer, nullable=False)

    rooms = relationship("Room", back_populates="category")


# -----------------------------
# ROOM
# -----------------------------
class Room(Base):
    """
    Номер: номер комнаты, категория, вместимость, цена.
    """
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    number = Column(Integer, unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    capacity = Column(Integer, nullable=False)
    price_per_night = Column(Integer, nullable=False)

    category = relationship("Category", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")


# -----------------------------
# CUSTOMER
# -----------------------------
class Customer(Base):
    """
    Клиент: ФИО, телефон, email.
    """
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)

    bookings = relationship("Booking", back_populates="customer")


# -----------------------------
# BOOKING
# -----------------------------
class Booking(Base):
    """
    Бронирование: даты, питание, скидки, итоговая сумма, статус.
    """
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))

    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(Date)

    guests_count = Column(Integer, default=1)

    # питание
    breakfast_count = Column(Integer, default=0)
    lunch_count = Column(Integer, default=0)
    dinner_count = Column(Integer, default=0)

    # скидки
    is_repeat_within_year = Column(Boolean, default=False)
    discount_nights = Column(Float, default=0.0)
    discount_repeat = Column(Float, default=0.0)

    total_amount = Column(Integer)
    final_amount = Column(Integer)

    status = Column(String)  # created | paid | cancelled

    room = relationship("Room", back_populates="bookings")
    customer = relationship("Customer", back_populates="bookings")

    payments = relationship(
        "Payment",
        back_populates="booking",
        cascade="all, delete-orphan"
    )


# -----------------------------
# PAYMENT
# -----------------------------
class Payment(Base):
    """
    Платёж: сумма, дата, метод, статус.
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))

    amount = Column(Integer)
    payment_date = Column(Date)
    method = Column(String)  # card | cash | online | bank
    status = Column(String)  # success | failed | cancelled

    booking = relationship("Booking", back_populates="payments")

    transactions = relationship(
        "Transaction",
        back_populates="payment",
        cascade="all, delete-orphan"
    )


# -----------------------------
# TRANSACTION
# -----------------------------
class Transaction(Base):
    """
    Транзакция: доход или возврат.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("payments.id"))

    amount = Column(Integer)
    transaction_date = Column(Date)
    type = Column(String)  # income | refund

    payment = relationship("Payment", back_populates="transactions")