# -*- coding: utf-8 -*-
"""
analysis.py — модуль анализа данных и построения графиков
"""

import os
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # использовать неблокирующий бэкенд (без GUI)

import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Booking, Room, Category

# Абсолютный путь к папке static/plots
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # папка app
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))  # корень проекта
PLOTS_DIR = os.path.join(PROJECT_DIR, "static", "plots")


def _ensure_plots_dir():
    if not os.path.exists(PLOTS_DIR):
        os.makedirs(PLOTS_DIR, exist_ok=True)


def _load_bookings_df(session: Session) -> pd.DataFrame:
    rows = (
        session.query(
            Booking.id,
            Booking.room_id,
            Booking.start_date,
            Booking.end_date,
            Booking.created_at,
            Booking.guests_count,
            Booking.final_amount,
            Booking.status,
        ).all()
    )
    df = pd.DataFrame(rows, columns=[
        "id", "room_id", "start_date", "end_date",
        "created_at", "guests_count", "final_amount", "status"
    ])
    if df.empty:
        return df
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["month"] = df["start_date"].dt.to_period("M").astype(str)
    return df


def _load_rooms_df(session: Session) -> pd.DataFrame:
    rows = session.query(Room.id, Room.number, Room.category_id).all()
    return pd.DataFrame(rows, columns=["room_id", "number", "category_id"])


def _load_categories_df(session: Session) -> pd.DataFrame:
    rows = session.query(Category.id, Category.name).all()
    return pd.DataFrame(rows, columns=["category_id", "category_name"])


def income_by_category(start_date=None, end_date=None):
    """Доходы по категориям за период"""
    _ensure_plots_dir()
    session: Session = SessionLocal()
    try:
        bdf = _load_bookings_df(session)
        if bdf.empty:
            return pd.DataFrame(), None

        if start_date:
            bdf = bdf[bdf["start_date"] >= pd.to_datetime(start_date)]
        if end_date:
            bdf = bdf[bdf["start_date"] <= pd.to_datetime(end_date)]

        rdf = _load_rooms_df(session)
        cdf = _load_categories_df(session)

        merged = bdf.merge(rdf, left_on="room_id", right_on="room_id", how="left")
        merged = merged.merge(cdf, on="category_id", how="left")
        merged["final_amount"] = merged["final_amount"].astype(float)

        df = merged.groupby("category_name")["final_amount"].sum().reset_index()
        df = df.rename(columns={"final_amount": "income"}).sort_values("income", ascending=False)

        filename = "plots/income_by_category.png"
        plot_path = os.path.join(PLOTS_DIR, "income_by_category.png")
        plt.figure(figsize=(8, 5))
        sns.barplot(data=df, x="category_name", y="income", color="#3b82f6")
        plt.title("Доходы по категориям")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

        return df, filename
    finally:
        session.close()


def guests_by_month():
    """Количество гостей по месяцам"""
    _ensure_plots_dir()
    session: Session = SessionLocal()
    try:
        bdf = _load_bookings_df(session)
        if bdf.empty:
            return pd.DataFrame(), None

        df = bdf.groupby("month")["guests_count"].sum().reset_index()
        df = df.rename(columns={"guests_count": "guests"}).sort_values("month")

        filename = "plots/guests_by_month.png"
        plot_path = os.path.join(PLOTS_DIR, "guests_by_month.png")
        plt.figure(figsize=(8, 5))
        sns.barplot(data=df, x="month", y="guests", color="#10b981")
        plt.title("Гости по месяцам")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

        return df, filename
    finally:
        session.close()


def top_rooms(limit=5):
    """Топ популярных номеров"""
    _ensure_plots_dir()
    session: Session = SessionLocal()
    try:
        bdf = _load_bookings_df(session)
        if bdf.empty:
            return pd.DataFrame(), None

        rdf = _load_rooms_df(session)
        cdf = _load_categories_df(session)

        counts = bdf.groupby("room_id")["id"].count().reset_index()
        counts = counts.rename(columns={"id": "bookings_count"})
        merged = counts.merge(rdf, on="room_id", how="left").merge(cdf, on="category_id", how="left")

        merged["room_label"] = merged.apply(
            lambda r: f"№{r['number']} ({r['category_name']})" if pd.notna(r["number"]) else f"Room {r['room_id']}",
            axis=1
        )
        df = merged.sort_values("bookings_count", ascending=False).head(limit)

        filename = "plots/top_rooms.png"
        plot_path = os.path.join(PLOTS_DIR, "top_rooms.png")
        plt.figure(figsize=(8, 5))
        sns.barplot(data=df, x="room_label", y="bookings_count", color="#f59e0b")
        plt.title(f"Топ-{limit} популярных номеров")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

        return df, filename
    finally:
        session.close()