from flask import Blueprint

gui_bp = Blueprint("gui", __name__)

@gui_bp.route("/")
def index():
    return "<h1>Приложение работает! Продолжаем разработку.</h1>"