# -*- coding: utf-8 -*-
"""
__init__.py — инициализация Flask-приложения
"""

import os
from flask import Flask, redirect, url_for, flash
from app.db import init_db
from app.gui import gui_bp
from app.client_routes import client_bp
from app.admin_routes import admin_bp


def create_app():
    """
    Фабрика приложения Flask.
    """
    # Абсолютный путь к корню проекта
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    static_dir = os.path.join(base_dir, "static")

    # Явно указываем Flask, где искать static/
    app = Flask(__name__, static_folder=static_dir)
    app.config.from_object("app.config.Config")
    app.secret_key = "supersecret"  # нужен для flash-сообщений

    # инициализация базы данных
    init_db()

    # регистрация blueprints
    app.register_blueprint(gui_bp)
    app.register_blueprint(client_bp, url_prefix="/client")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # обработчик ошибок 400 — редиректит на форму бронирования клиента
    @app.errorhandler(400)
    def bad_request(e):
        flash(f"Некорректный запрос: {getattr(e, 'description', str(e))}")
        return redirect(url_for("client.client_booking_form"))

    return app