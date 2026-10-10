from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import TrafficRecord, User


router = APIRouter(
    prefix="/traffic",
    tags=["Traffic"],
)


def build_traffic_conditions(
    start_date: datetime | None,
    end_date: datetime | None,
    weather: str | None,
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before end_date",
        )

    conditions = []

    if start_date:
        conditions.append(
            TrafficRecord.date_time >= start_date
        )

    if end_date:
        conditions.append(
            TrafficRecord.date_time <= end_date
        )

    if weather:
        conditions.append(
            func.lower(TrafficRecord.weather_main)
            == weather.lower()
        )

    return conditions


@router.get("/summary")
def get_traffic_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = db.execute(
        select(
            func.count(TrafficRecord.id),
            func.avg(TrafficRecord.traffic_volume),
            func.min(TrafficRecord.traffic_volume),
            func.max(TrafficRecord.traffic_volume),
        )
    ).one()

    total_records, average_volume, min_volume, max_volume = result

    return {
        "total_records": total_records,
        "average_traffic_volume": round(
            float(average_volume),
            2,
        ),
        "minimum_traffic_volume": min_volume,
        "maximum_traffic_volume": max_volume,
    }


@router.get("/hourly")
def get_hourly_traffic(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    weather: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conditions = build_traffic_conditions(
        start_date,
        end_date,
        weather,
    )

    hour = extract(
        "hour",
        TrafficRecord.date_time,
    ).label("hour")

    average_volume = func.avg(
        TrafficRecord.traffic_volume
    ).label("average_traffic_volume")

    query = select(
        hour,
        average_volume,
    )

    if conditions:
        query = query.where(*conditions)

    query = (
        query
        .group_by(hour)
        .order_by(hour)
    )

    results = db.execute(query).all()

    return [
        {
            "hour": int(row.hour),
            "average_traffic_volume": round(
                float(row.average_traffic_volume),
                2,
            ),
        }
        for row in results
    ]


@router.get("/peak-hours")
def get_peak_hours(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    hour = extract(
        "hour",
        TrafficRecord.date_time,
    ).label("hour")

    average_volume = func.avg(
        TrafficRecord.traffic_volume
    ).label("average_traffic_volume")

    results = db.execute(
        select(
            hour,
            average_volume,
        )
        .group_by(hour)
        .order_by(average_volume.desc())
        .limit(5)
    ).all()

    return [
        {
            "hour": int(row.hour),
            "average_traffic_volume": round(
                float(row.average_traffic_volume),
                2,
            ),
        }
        for row in results
    ]


@router.get("/weekday")
def get_weekday_traffic(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    weather: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conditions = build_traffic_conditions(
        start_date,
        end_date,
        weather,
    )

    day_number = extract(
        "isodow",
        TrafficRecord.date_time,
    ).label("day_number")

    average_volume = func.avg(
        TrafficRecord.traffic_volume
    ).label("average_traffic_volume")

    query = select(
        day_number,
        average_volume,
    )

    if conditions:
        query = query.where(*conditions)

    query = (
        query
        .group_by(day_number)
        .order_by(day_number)
    )

    results = db.execute(query).all()

    day_names = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday",
    }

    return [
        {
            "day": day_names[int(row.day_number)],
            "average_traffic_volume": round(
                float(row.average_traffic_volume),
                2,
            ),
        }
        for row in results
    ]


@router.get("/weather")
def get_weather_traffic(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    weather: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conditions = build_traffic_conditions(
        start_date,
        end_date,
        weather,
    )

    average_volume = func.avg(
        TrafficRecord.traffic_volume
    ).label("average_traffic_volume")

    record_count = func.count(
        TrafficRecord.id
    ).label("record_count")

    query = select(
        TrafficRecord.weather_main,
        average_volume,
        record_count,
    )

    if conditions:
        query = query.where(*conditions)

    query = (
        query
        .group_by(TrafficRecord.weather_main)
        .order_by(average_volume.desc())
    )

    results = db.execute(query).all()

    return [
        {
            "weather": row.weather_main,
            "average_traffic_volume": round(
                float(row.average_traffic_volume),
                2,
            ),
            "record_count": row.record_count,
        }
        for row in results
    ]


@router.get("/filter-summary")
def get_filtered_traffic_summary(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    weather: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conditions = build_traffic_conditions(
        start_date,
        end_date,
        weather,
    )

    query = select(
        func.count(TrafficRecord.id),
        func.avg(TrafficRecord.traffic_volume),
        func.min(TrafficRecord.traffic_volume),
        func.max(TrafficRecord.traffic_volume),
    )

    if conditions:
        query = query.where(*conditions)

    result = db.execute(query).one()

    total_records, average_volume, min_volume, max_volume = result

    return {
        "total_records": total_records,
        "average_traffic_volume": (
            round(float(average_volume), 2)
            if average_volume is not None
            else None
        ),
        "minimum_traffic_volume": min_volume,
        "maximum_traffic_volume": max_volume,
    }


@router.get("/weather-options")
def get_weather_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = db.scalars(
        select(TrafficRecord.weather_main)
        .distinct()
        .order_by(TrafficRecord.weather_main)
    ).all()

    return {
        "weather_options": results,
    }


@router.get("/date-range")
def get_date_range(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = db.execute(
        select(
            func.min(TrafficRecord.date_time),
            func.max(TrafficRecord.date_time),
        )
    ).one()

    start_date, end_date = result

    return {
        "start_date": start_date,
        "end_date": end_date,
    }