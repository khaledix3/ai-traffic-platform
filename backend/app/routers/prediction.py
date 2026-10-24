from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..dependencies import get_current_user
from ..ml_service import predict_traffic_volume
from ..models import User


router = APIRouter(tags=["AI Predictions"])


class PredictionRequest(BaseModel):
    date_time: datetime
    temp: float = Field(gt=0, le=350)
    rain_1h: float = Field(default=0, ge=0)
    snow_1h: float = Field(default=0, ge=0)
    clouds_all: int = Field(ge=0, le=100)

    weather_main: Literal[
        "Clear",
        "Clouds",
        "Drizzle",
        "Fog",
        "Haze",
        "Mist",
        "Rain",
        "Smoke",
        "Snow",
        "Squall",
        "Thunderstorm",
    ]

    holiday: str = "None"


@router.post("/predict")
def predict_traffic(
    data: PredictionRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        prediction = predict_traffic_volume(
            date_time=data.date_time,
            temp=data.temp,
            rain_1h=data.rain_1h,
            snow_1h=data.snow_1h,
            clouds_all=data.clouds_all,
            weather_main=data.weather_main,
            holiday=data.holiday,
        )

    except (FileNotFoundError, OSError, KeyError, ValueError):
        raise HTTPException(
            status_code=503,
            detail="Prediction model is unavailable",
        )

    return {
        "predicted_traffic_volume": prediction,
        "unit": "vehicles/hour",
    }