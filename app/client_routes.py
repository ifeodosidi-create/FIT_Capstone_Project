# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Room, Customer
from app.services.booking_service import calculate_booking, create_booking

client_bp = Blueprint("client", __name__)

def _load_form_lists(session: Session):
    rooms = session.query(Room).all()
    customers = session.query(Customer).all()
    return rooms, customers

def _parse_dates(start: str, end: str):
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None, None, "Неверный формат даты."
    if end_date <= start_date:
        return None, None, "Дата выезда должна быть позже даты заезда."
    return start_date, end_date, None

def _build_data(form):
    room_id = form.get("room_id")
    start = form.get("start_date")
    end = form.get("end_date")
    if not room_id or not start or not end:
        return None, "Не хватает данных."
    start_date, end_date, err = _parse_dates(start, end)
    if err:
        return None, err
    nights = (end_date - start_date).days
    try:
        return {
            "room_id": int(room_id),
            "nights": nights,
            "guests_count": int(form.get("guests_count", "1")),
            "lunch_count": int(form.get("lunch_count", "0")),
            "dinner_count": int(form.get("dinner_count", "0")),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }, None
    except ValueError:
        return None, "Некорректные числовые значения."

# -----------------------------
# Форма брони
# -----------------------------
@client_bp.route("/booking/form", methods=["GET"])
def client_booking_form():
    session: Session = SessionLocal()
    try:
        rooms, customers = _load_form_lists(session)
        return render_template("client_create.html", rooms=rooms, customers=customers)
    finally:
        session.close()

# -----------------------------
# Первый шаг: показать расчёт и кнопку подтверждения
# -----------------------------
@client_bp.route("/booking/preview", methods=["POST"])
def client_booking_preview():
    data, err = _build_data(request.form)
    if err:
        flash(err)
        return redirect(url_for("client.client_booking_form"))

    customer_id = request.form.get("customer_id", "new")
    full_name = request.form.get("full_name")
    phone = request.form.get("phone")
    email = request.form.get("email")

    if customer_id != "new":
        try:
            data["customer_id"] = int(customer_id)
        except ValueError:
            flash("Некорректный идентификатор клиента.")
            return redirect(url_for("client.client_booking_form"))
    else:
        # новый клиент — обязательно ФИО и телефон
        if not full_name or not phone:
            flash("Для нового клиента укажите ФИО и телефон.")
            return redirect(url_for("client.client_booking_form"))
        data["customer_id"] = None
        data["full_name"] = full_name
        data["phone"] = phone
        if email:
            data["email"] = email

    try:
        result = calculate_booking(data)
    except Exception as e:
        flash(f"Ошибка расчёта: {e}")
        return redirect(url_for("client.client_booking_form"))

    return render_template("client_preview.html", data=data, result=result)

# -----------------------------
# Второй шаг: подтверждение и сохранение
# -----------------------------
@client_bp.route("/booking/confirm", methods=["POST"])
def client_booking_confirm():
    data = dict(request.form)
    try:
        result = create_booking(data)
    except Exception as e:
        flash(f"Ошибка создания брони: {e}")
        return redirect(url_for("client.client_booking_form"))
    return render_template("client_result.html", result=result)