# app/admin_routes.py

from flask import Blueprint, jsonify
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Booking, Payment, Transaction, Room, Customer

admin_bp = Blueprint("admin", __name__)


# -----------------------------
# GET ALL BOOKINGS
# -----------------------------
@admin_bp.route("/bookings", methods=["GET"])
def get_bookings():
    """
    Возвращает список всех бронирований.
    """
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

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()


# -----------------------------
# GET ALL PAYMENTS
# -----------------------------
@admin_bp.route("/payments", methods=["GET"])
def get_payments():
    """
    Возвращает список всех платежей.
    """
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

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()


# -----------------------------
# GET ALL TRANSACTIONS
# -----------------------------
@admin_bp.route("/transactions", methods=["GET"])
def get_transactions():
    """
    Возвращает список всех транзакций.
    """
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

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()