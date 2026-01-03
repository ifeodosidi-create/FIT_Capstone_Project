from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.db import Base


# -----------------------------
# CATEGORY
# -----------------------------
class Category(Base):
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
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    total_amount = Column(Integer)
    status = Column(String)

    # количество гостей
    guests_count = Column(Integer, default=1)

    # питание (количество порций)
    breakfast_count = Column(Integer, default=0)
    lunch_count = Column(Integer, default=0)
    dinner_count = Column(Integer, default=0)

    # скидки
    discount_nights = Column(Float, default=0.0)
    discount_repeat = Column(Float, default=0.0)
    final_amount = Column(Integer)

    room = relationship("Room", back_populates="bookings")
    customer = relationship("Customer", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")



# -----------------------------
# PAYMENT
# -----------------------------
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    amount = Column(Integer)
    payment_date = Column(Date)
    method = Column(String)  # cash | card | online | bank

    booking = relationship("Booking", back_populates="payments")
    transactions = relationship("Transaction", back_populates="payment")


# -----------------------------
# TRANSACTION
# -----------------------------
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("payments.id"))
    amount = Column(Integer)
    transaction_date = Column(Date)
    type = Column(String)  # income | refund

    payment = relationship("Payment", back_populates="transactions")