from app.db import engine

print("Драйвер:", engine.name)
print("URL:", engine.url)