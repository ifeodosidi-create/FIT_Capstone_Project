from flask import Flask
from app.db import init_db
from app.gui import gui_bp
from app.client import client_bp   # ✅ без routes
from app.admin import admin_bp     # ✅ без routes

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # инициализация базы данных
    init_db()

    # регистрация blueprints
    app.register_blueprint(gui_bp)
    app.register_blueprint(client_bp, url_prefix="/client")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app