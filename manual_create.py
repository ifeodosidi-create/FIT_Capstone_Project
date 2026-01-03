# manual_create.py
from app.db import Base, engine
import app.models  # важно: импортировать, чтобы модели зарегистрировались в Base

def recreate_all():
    print("Удаляю все таблицы...")
    Base.metadata.drop_all(bind=engine)
    print("Создаю таблицы по текущим моделям...")
    Base.metadata.create_all(bind=engine)
    print("Готово!")

if __name__ == "__main__":
    recreate_all()