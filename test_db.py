from app.db import Base, engine
import app.models

print("Создаю таблицы вручную...")
Base.metadata.create_all(bind=engine)
print("Готово!")