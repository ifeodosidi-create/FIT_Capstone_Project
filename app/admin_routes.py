# -*- coding: utf-8 -*-
"""
admin_routes.py — маршруты для администратора:
- просмотр всех данных (bookings, payments, transactions)
- экспорт в JSON/CSV
- запуск анализа и построение графиков
"""

import csv
from flask import Blueprint, jsonify, render_template, request, Response, url_for
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Booking, Payment, Transaction
from app.analysis import income_by_category, guests_by_month, top_rooms

admin_bp = Blueprint("admin", __name__, template_folder="templates")


# -----------------------------
# BOOKINGS JSON + CSV
# -----------------------------
@admin_bp.route("/bookings", methods=["GET"])
def get_bookings():
    """Возвращает список всех бронирований (JSON)."""
    session: Session = SessionLocal()
    try:
        bookings = session.query(Booking).all()
        result = []
        for b in bookings:
            result.append({
                "id": b.id,
                "room_id": b.room_id,
                "customer_id": b.customer_id,
                "start_date": b.start_date.isoformat() if b.start_date else None,
                "end_date": b.end_date.isoformat() if b.end_date else None,
                "guests_count": b.guests_count,
                "total_amount": b.total_amount,
                "final_amount": b.final_amount,
                "status": b.status,
                "created_at": b.created_at.isoformat() if b.created_at else None
            })
        return render_template("bookings_json.html", bookings=result)
    finally:
        session.close()


@admin_bp.route("/download/bookings.csv")
def download_bookings_csv():
    """Выгрузка всех бронирований в CSV."""
    session = SessionLocal()
    try:
        rows = session.query(Booking).all()
        header = ["id", "room_id", "customer_id", "start_date", "end_date",
                  "guests_count", "total_amount", "final_amount", "status", "created_at"]

        def generate():
            yield ",".join(header) + "\n"
            for b in rows:
                yield ",".join([
                    str(b.id),
                    str(b.room_id),
                    str(b.customer_id),
                    str(b.start_date),
                    str(b.end_date),
                    str(b.guests_count),
                    str(b.total_amount),
                    str(b.final_amount),
                    str(b.status),
                    str(b.created_at)
                ]) + "\n"

        return Response(generate(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=bookings.csv"})
    finally:
        session.close()


# -----------------------------
# PAYMENTS JSON + CSV
# -----------------------------
@admin_bp.route("/payments", methods=["GET"])
def get_payments():
    """Возвращает список всех платежей (JSON)."""
    session: Session = SessionLocal()
    try:
        payments = session.query(Payment).all()
        result = []
        for p in payments:
            result.append({
                "id": p.id,
                "booking_id": p.booking_id,
                "amount": p.amount,
                "method": p.method,
                "status": p.status,
                "payment_date": p.payment_date.isoformat() if p.payment_date else None
            })
        return render_template("payments_json.html", payments=result)
    finally:
        session.close()


@admin_bp.route("/download/payments.csv")
def download_payments_csv():
    """Выгрузка всех платежей в CSV."""
    session = SessionLocal()
    try:
        rows = session.query(Payment).all()
        header = ["id", "booking_id", "amount", "method", "status", "payment_date"]

        def generate():
            yield ",".join(header) + "\n"
            for p in rows:
                yield ",".join([
                    str(p.id),
                    str(p.booking_id),
                    str(p.amount),
                    str(p.method),
                    str(p.status),
                    str(p.payment_date)
                ]) + "\n"

        return Response(generate(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=payments.csv"})
    finally:
        session.close()


# -----------------------------
# TRANSACTIONS JSON + CSV
# -----------------------------
@admin_bp.route("/transactions", methods=["GET"])
def get_transactions():
    """Возвращает список всех транзакций (JSON)."""
    session: Session = SessionLocal()
    try:
        transactions = session.query(Transaction).all()
        result = []
        for t in transactions:
            result.append({
                "id": t.id,
                "payment_id": t.payment_id,
                "amount": t.amount,
                "type": t.type,
                "transaction_date": t.transaction_date.isoformat() if t.transaction_date else None
            })
        return render_template("transactions_json.html", transactions=result)
    finally:
        session.close()


@admin_bp.route("/download/transactions.csv")
def download_transactions_csv():
    """Выгрузка всех транзакций в CSV."""
    session = SessionLocal()
    try:
        rows = session.query(Transaction).all()
        header = ["id", "payment_id", "amount", "type", "transaction_date"]

        def generate():
            yield ",".join(header) + "\n"
            for t in rows:
                yield ",".join([
                    str(t.id),
                    str(t.payment_id),
                    str(t.amount),
                    str(t.type),
                    str(t.transaction_date)
                ]) + "\n"

        return Response(generate(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=transactions.csv"})
    finally:
        session.close()


# -----------------------------
# ADMIN DASHBOARD (ANALYSIS + GRAPHS)
# -----------------------------
@admin_bp.route("/dashboard", methods=["GET"])
def admin_dashboard():
    """Страница анализа: доходы по категориям, гости по месяцам, топ-5 номеров."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    income_df, income_plot = income_by_category(start_date, end_date)
    guests_df, guests_plot = guests_by_month()
    top_df, top_plot = top_rooms(limit=5)

    return render_template(
        "admin_dashboard.html",
        income_df=income_df.to_dict(orient="records") if not income_df.empty else [],
        income_plot=income_plot,
        guests_df=guests_df.to_dict(orient="records") if not guests_df.empty else [],
        guests_plot=guests_plot,
        top_df=top_df.to_dict(orient="records") if not top_df.empty else [],
        top_plot=top_plot,
        start_date=start_date or "",
        end_date=end_date or ""
    )