from app.db import Base
import app.models

print("Найденные модели:")
print(list(Base.metadata.tables.keys()))