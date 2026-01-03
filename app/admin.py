from flask import Blueprint, jsonify

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/bookings", methods=["GET"])
def get_bookings():
    return jsonify({"message": "Список бронирований (заглушка)"})