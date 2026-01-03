from flask import Flask
from app.db import init_db
from app.gui import gui_bp
from app.client_routes import client_bp
from app.admin_routes import admin_bp


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