import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd


MODEL_DIR = Path(__file__).resolve().parent / "ml"
MODEL_PATH = MODEL_DIR / "traffic_ridge_model.npz"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

NUMERIC_COLUMNS = [
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",
]

CATEGORICAL_COLUMNS = [
    "holiday",
    "weather_main",
    "hour",
    "weekday",
    "month",
]


@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError(
            "Trained model files are missing. Run train_model.py first."
        )

    with np.load(MODEL_PATH, allow_pickle=False) as model:
        weights = model["weights"].copy()

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    return weights, metadata


def predict_traffic_volume(
    *,
    date_time: datetime,
    temp: float,
    rain_1h: float,
    snow_1h: float,
    clouds_all: int,
    weather_main: str,
    holiday: str = "None",
):
    weights, metadata = load_model()

    data = pd.DataFrame([{
        "temp": temp,
        "rain_1h": rain_1h,
        "snow_1h": snow_1h,
        "clouds_all": clouds_all,
        "holiday": holiday,
        "weather_main": weather_main,
        "hour": date_time.hour,
        "weekday": date_time.weekday(),
        "month": date_time.month,
    }])

    for column in NUMERIC_COLUMNS:
        mean = metadata["numeric_means"][column]
        std = metadata["numeric_stds"][column]

        data[column] = (data[column] - mean) / std

    features = pd.get_dummies(
        data,
        columns=CATEGORICAL_COLUMNS,
        dtype=float,
    )

    features = features.reindex(
        columns=metadata["feature_names"],
        fill_value=0.0,
    )

    X = features.to_numpy(dtype=float)

    X_with_intercept = np.column_stack([
        np.ones(len(X)),
        X,
    ])

    prediction = float((X_with_intercept @ weights)[0])

    return round(max(0.0, prediction))