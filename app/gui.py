from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import Session
from datetime import datetime, date
import re

from app.db import SessionLocal
from app.models import Room, Customer, Booking, Payment
from app.services.booking_service import calculate_booking, create_booking

# Папка templates ожидается в корне проекта (../templates относительно app/)
gui_bp = Blueprint("gui", __name__, template_folder="../templates")


@gui_bp.route("/", methods=["GET"])
def index():
    return render_template("layout.html")


# -----------------------------
# Создание брони (с проверкой и возможностью создания нового клиента)
# -----------------------------
@gui_bp.route("/client/booking/create", methods=["GET", "POST"])
def gui_client_create():
    session: Session = SessionLocal()
    try:
        if request.method == "GET":
            rooms = session.query(Room).all()
            customers = session.query(Customer).all()
            return render_template("client_create.html", rooms=rooms, customers=customers)

        data = request.form

        # Проверка телефона и email
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        full_name = data.get("full_name", "").strip()

        if not re.fullmatch(r"^\+?\d{10,15}$", phone):
            flash("Некорректный телефон. Разрешены только цифры и +, длина 10–15.", "error")
            return redirect(url_for("gui.gui_client_create"))

        if not re.fullmatch(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            flash("Некорректный email.", "error")
            return redirect(url_for("gui.gui_client_create"))

        # Основные поля
        room_id = int(data["room_id"])
        base_price = float(data["base_price_per_night"])
        guests = int(data["guests_count"])

        # Проверка вместимости
        room = session.query(Room).filter_by(id=room_id).first()
        if not room:
            flash("Комната не найдена.", "error")
            return redirect(url_for("gui.gui_client_create"))
        if guests > room.capacity:
            flash(f"Количество гостей ({guests}) превышает вместимость номера ({room.capacity}).", "error")
            return redirect(url_for("gui.gui_client_create"))

        # Даты и ночи
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        nights = (end_date - start_date).days
        if nights <= 0:
            flash("Дата выезда должна быть позже даты заезда (минимум 1 ночь).", "error")
            return redirect(url_for("gui.gui_client_create"))

        # Питание
        lunch_count = int(data.get("lunch_count", 0))
        dinner_count = int(data.get("dinner_count", 0))
        if lunch_count < 0 or dinner_count < 0:
            flash("Количество обедов/ужинов не может быть отрицательным.", "error")
            return redirect(url_for("gui.gui_client_create"))

        # Клиент
        customer_selector = data.get("customer_id")
        if customer_selector and customer_selector != "new":
            customer_id = int(customer_selector)
        else:
            if not full_name:
                flash("Для нового клиента укажите ФИО.", "error")
                return redirect(url_for("gui.gui_client_create"))
            new_customer = Customer(full_name=full_name, phone=phone, email=email)
            session.add(new_customer)
            session.commit()
            customer_id = new_customer.id

        # Создание брони
        booking_data = {
            "base_price_per_night": base_price,
            "guests_count": guests,
            "nights": nights,
            "lunch_count": lunch_count,
            "dinner_count": dinner_count,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "customer_id": customer_id,
            "room_id": room_id,
        }

        result = create_booking(booking_data)
        flash(f"Бронь создана. ID: {result['booking_id']}", "success")
        return render_template("client_result.html", result=result)

    except Exception as e:
        flash(f"Ошибка: {e}", "error")
        return redirect(url_for("gui.gui_client_create"))
    finally:
        session.close()


# -----------------------------
# Расчёт стоимости бронирования
# -----------------------------
@gui_bp.route("/client/booking/calculate", methods=["POST"])
def gui_client_calculate():
    try:
        data = request.form
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        nights = (end_date - start_date).days
        if nights <= 0:
            flash("Дата выезда должна быть позже даты заезда.", "error")
            return redirect(url_for("gui.index"))

        booking_data = {
            "base_price_per_night": float(data["base_price_per_night"]),
            "guests_count": int(data["guests_count"]),
            "nights": nights,
            "lunch_count": int(data.get("lunch_count", 0)),
            "dinner_count": int(data.get("dinner_count", 0)),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }
        result = calculate_booking(booking_data)
        return render_template("client_result.html", result=result)

    except Exception as e:
        flash(f"Ошибка: {e}", "error")
        return redirect(url_for("gui.index"))


# -----------------------------
# Оплата брони
# -----------------------------
@gui_bp.route("/client/booking/pay", methods=["GET", "POST"])
def gui_client_pay():
    session: Session = SessionLocal()
    try:
        if request.method == "GET":
            return render_template("client_pay.html")

        booking_id = int(request.form["booking_id"])
        method = request.form.get("method", "card")
        confirm = request.form.get("confirm") == "yes"

        booking = session.query(Booking).filter_by(id=booking_id).first()
        if not booking:
            flash("Бронь не найдена", "error")
            return redirect(url_for("gui.gui_client_pay"))

        if not confirm:
            flash("Здесь должен быть эквайринг. Подтвердите платеж.", "info")
            return redirect(url_for("gui.gui_client_pay"))

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

        result = {"booking_id": booking_id, "payment_id": payment.id, "status": "paid"}
        return render_template("client_result.html", result=result)

    except Exception as e:
        flash(f"Ошибка: {e}", "error")
        return redirect(url_for("gui.gui_client_pay"))
    finally:
        session.close()


# -----------------------------
# Отмена брони
# -----------------------------
@gui_bp.route("/client/booking/cancel", methods=["GET", "POST"])
def gui_client_cancel():
    session: Session = SessionLocal()
    try:
        if request.method == "GET":
            return render_template("client_cancel.html")

        booking_id = int(request.form["booking_id"])
        booking = session.query(Booking).filter_by(id=booking_id).first()
        if not booking:
            flash("Бронь не найдена", "error")
            return redirect(url_for("gui.gui_client_cancel"))

        if booking.start_date <= date.today():
            flash("Отмена невозможна: до заезда меньше 1 дня", "error")
            return redirect(url_for("gui.gui_client_cancel"))

        was_paid = booking.status == "paid"
        booking.status = "cancelled"
        session.commit()

        msg = {"booking_id": booking_id, "status": "cancelled"}
        if was_paid:
            msg["message"] = "За возвратом денежных средств обращайтесь по телефону 880012345678"
        return render_template("client_result.html", result=msg)

    except Exception as e:
        flash(f"Ошибка: {e}", "error")
        return redirect(url_for("gui.gui_client_cancel"))
    finally:
        session.close()