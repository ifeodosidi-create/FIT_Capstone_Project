from sqlalchemy import inspect
from app.db import engine

insp = inspect(engine)

print("Схемы:", insp.get_schema_names())

for schema in insp.get_schema_names():
    print(f"\nТаблицы в схеме '{schema}':")
    try:
        print(insp.get_table_names(schema=schema))
    except Exception as e:
        print("Ошибка:", e)