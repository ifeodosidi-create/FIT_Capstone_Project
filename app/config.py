import os

class Config:
    # строка подключения к PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://hotel_user:12345@localhost/hotel_finance"
    )

    # отключаем лишние уведомления SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # секретный ключ для Flask (используется для сессий и форм)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")

    # дополнительные настройки (по желанию)
    DEBUG = True
