from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import Config

# Создаём движок SQLAlchemy
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# Создаём фабрику сессий
SessionLocal = sessionmaker(bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def init_db():
    try:
        # Импортируем МОДУЛЬ моделей, чтобы SQLAlchemy зарегистрировал все классы
        import app.models

        # Создаём таблицы
        Base.metadata.create_all(bind=engine)
        print("База данных инициализирована.")
    except Exception as e:
        print(f"Ошибка инициализации базы данных: {e}")