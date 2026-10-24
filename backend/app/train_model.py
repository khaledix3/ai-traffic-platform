import json
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import select

from .database import engine
from .models import TrafficRecord


MODEL_DIR = Path(__file__).resolve().parent / "ml"
MODEL_PATH = MODEL_DIR / "traffic_ridge_model.npz"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

RIDGE_ALPHA = 10.0

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


def load_data():
    query = select(
        TrafficRecord.holiday,
        TrafficRecord.temp,
        TrafficRecord.rain_1h,
        TrafficRecord.snow_1h,
        TrafficRecord.clouds_all,
        TrafficRecord.weather_main,
        TrafficRecord.date_time,
        TrafficRecord.traffic_volume,
    )

    return pd.read_sql(query, engine)


def prepare_data(df):
    df = df.copy()

    df["date_time"] = pd.to_datetime(df["date_time"])

    df["holiday"] = df["holiday"].fillna("None")

    df["hour"] = df["date_time"].dt.hour
    df["weekday"] = df["date_time"].dt.dayofweek
    df["month"] = df["date_time"].dt.month

    df = df.sort_values(
        "date_time"
    ).reset_index(drop=True)

    return df


def split_by_time(df):
    split_index = int(len(df) * 0.80)

    cutoff_time = df.iloc[
        split_index
    ]["date_time"]

    train_df = df[
        df["date_time"] < cutoff_time
    ].copy()

    test_df = df[
        df["date_time"] >= cutoff_time
    ].copy()

    return train_df, test_df, cutoff_time


def standardize_numeric(
    train_df,
    test_df,
):
    means = {}
    stds = {}

    for column in NUMERIC_COLUMNS:
        mean = float(train_df[column].mean())
        std = float(train_df[column].std())

        if std == 0:
            std = 1.0

        means[column] = mean
        stds[column] = std

        train_df[column] = (
            train_df[column] - mean
        ) / std

        test_df[column] = (
            test_df[column] - mean
        ) / std

    return train_df, test_df, means, stds


def build_features(
    train_df,
    test_df,
):
    train_features = pd.get_dummies(
        train_df[
            NUMERIC_COLUMNS + CATEGORICAL_COLUMNS
        ],
        columns=CATEGORICAL_COLUMNS,
        dtype=float,
    )

    test_features = pd.get_dummies(
        test_df[
            NUMERIC_COLUMNS + CATEGORICAL_COLUMNS
        ],
        columns=CATEGORICAL_COLUMNS,
        dtype=float,
    )

    test_features = test_features.reindex(
        columns=train_features.columns,
        fill_value=0.0,
    )

    return train_features, test_features


def fit_ridge_regression(
    X,
    y,
    alpha,
):
    X_with_intercept = np.column_stack(
        [
            np.ones(len(X)),
            X,
        ]
    )

    identity = np.eye(
        X_with_intercept.shape[1]
    )

    identity[0, 0] = 0.0

    left_side = (
        X_with_intercept.T
        @ X_with_intercept
        + alpha * identity
    )

    right_side = (
        X_with_intercept.T
        @ y
    )

    weights = np.linalg.solve(
        left_side,
        right_side,
    )

    return weights


def predict(X, weights):
    X_with_intercept = np.column_stack(
        [
            np.ones(len(X)),
            X,
        ]
    )

    return X_with_intercept @ weights


def calculate_metrics(
    actual,
    predicted,
):
    errors = actual - predicted

    mae = np.mean(
        np.abs(errors)
    )

    rmse = np.sqrt(
        np.mean(errors ** 2)
    )

    total_variance = np.sum(
        (actual - np.mean(actual)) ** 2
    )

    residual_variance = np.sum(
        errors ** 2
    )

    r2 = 1 - (
        residual_variance / total_variance
    )

    return mae, rmse, r2


def train_model():
    print("Loading data from PostgreSQL...")

    df = load_data()
    df = prepare_data(df)

    train_df, test_df, cutoff_time = split_by_time(
        df
    )

    train_df, test_df, means, stds = (
        standardize_numeric(
            train_df,
            test_df,
        )
    )

    X_train_df, X_test_df = build_features(
        train_df,
        test_df,
    )

    X_train = X_train_df.to_numpy(
        dtype=float
    )

    X_test = X_test_df.to_numpy(
        dtype=float
    )

    y_train = train_df[
        "traffic_volume"
    ].to_numpy(dtype=float)

    y_test = test_df[
        "traffic_volume"
    ].to_numpy(dtype=float)

    print()
    print("Total rows:", len(df))
    print("Training rows:", len(train_df))
    print("Testing rows:", len(test_df))

    print()
    print(
        "Training period:",
        train_df["date_time"].min(),
        "->",
        train_df["date_time"].max(),
    )

    print(
        "Testing period:",
        test_df["date_time"].min(),
        "->",
        test_df["date_time"].max(),
    )

    print()
    print(
        "Number of features:",
        X_train.shape[1],
    )

    print()
    print("Training Ridge Regression...")

    weights = fit_ridge_regression(
        X_train,
        y_train,
        RIDGE_ALPHA,
    )

    predictions = predict(
        X_test,
        weights,
    )

    mae, rmse, r2 = calculate_metrics(
        y_test,
        predictions,
    )

    baseline_predictions = np.full(
        len(y_test),
        np.mean(y_train),
    )

    baseline_mae = np.mean(
        np.abs(
            y_test - baseline_predictions
        )
    )

    print()
    print("MODEL RESULTS")
    print("----------------------------")
    print(f"MAE: {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²: {r2:.4f}")
    print(f"Baseline MAE: {baseline_mae:.2f}")

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    np.savez(
        MODEL_PATH,
        weights=weights,
    )

    metadata = {
        "model_type": "Ridge Regression",
        "ridge_alpha": RIDGE_ALPHA,
        "total_rows": len(df),
        "training_rows": len(train_df),
        "testing_rows": len(test_df),
        "cutoff_time": cutoff_time.isoformat(),
        "feature_names": X_train_df.columns.tolist(),
        "numeric_means": means,
        "numeric_stds": stds,
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "baseline_mae": float(baseline_mae),
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
        )

    print()
    print("Model saved successfully.")
    print("Model:", MODEL_PATH)
    print("Metadata:", METADATA_PATH)


if __name__ == "__main__":
    train_model()