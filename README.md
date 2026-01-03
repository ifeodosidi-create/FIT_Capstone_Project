# FIT Capstone Project

Учебный проект для управления бронированиями номеров в отеле.

Web-приложение на Pytone, БД - Postgres

##  Возможности
- Просмотр списка номеров
- Расчёт стоимости брони;
- Бронирование номера с выбором категории и услуг 
- Оплата брони
- Отмена брони
- Админские маршруты
- Аналитика данных для хозяина (pandas, seaborn)

## Установка и запуск
```bash
# Клонируем репозиторий
git clone https://github.com/<username>/FIT_Capstone_Project.git
cd FIT_Capstone_Project

# Создаём виртуальное окружение
python -m venv venv
venv\Scripts\activate   # Windows

# Устанавливаем зависимости
pip install -r requirements.txt

# Запускаем сервер
python main.py