from fastapi import APIRouter, Depends
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import TrafficRecord, User


router = APIRouter(
    prefix="/traffic",
    tags=["Traffic"],
)


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
        "average_traffic_volume": round(float(average_volume), 2),
        "minimum_traffic_volume": min_volume,
        "maximum_traffic_volume": max_volume,
    }


@router.get("/hourly")
def get_hourly_traffic(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    hour = extract("hour", TrafficRecord.date_time)

    results = db.execute(
        select(
            hour.label("hour"),
            func.avg(TrafficRecord.traffic_volume).label(
                "average_traffic_volume"
            ),
        )
        .group_by(hour)
        .order_by(hour)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    day_number = extract(
        "isodow",
        TrafficRecord.date_time,
    ).label("day_number")

    average_volume = func.avg(
        TrafficRecord.traffic_volume
    ).label("average_traffic_volume")

    results = db.execute(
        select(
            day_number,
            average_volume,
        )
        .group_by(day_number)
        .order_by(day_number)
    ).all()

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    average_volume = func.avg(
        TrafficRecord.traffic_volume
    ).label("average_traffic_volume")

    record_count = func.count(
        TrafficRecord.id
    ).label("record_count")

    results = db.execute(
        select(
            TrafficRecord.weather_main,
            average_volume,
            record_count,
        )
        .group_by(TrafficRecord.weather_main)
        .order_by(average_volume.desc())
    ).all()

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