from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class TrafficRecord(Base):
    __tablename__ = "traffic_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    holiday: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    temp: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    rain_1h: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    snow_1h: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    clouds_all: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    weather_main: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    weather_description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    date_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    traffic_volume: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )