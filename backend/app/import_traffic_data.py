import pandas as pd

from sqlalchemy import func, insert, select
from ucimlrepo import fetch_ucirepo

from .database import SessionLocal
from .models import TrafficRecord


def load_and_clean_traffic_data():
    dataset = fetch_ucirepo(id=492)

    df = pd.concat(
        [dataset.data.features, dataset.data.targets],
        axis=1,
    )

    df["holiday"] = df["holiday"].where(
        df["holiday"].notna(),
        None,
    )

    df["date_time"] = pd.to_datetime(df["date_time"])

    return df


def import_traffic_data():
    df = load_and_clean_traffic_data()

    db = SessionLocal()

    try:
        existing_rows = db.scalar(
            select(func.count()).select_from(TrafficRecord)
        )

        if existing_rows > 0:
            print(
                f"Import cancelled: traffic_records already "
                f"contains {existing_rows} rows."
            )
            return

        records = []

        for row in df.itertuples(index=False):
            records.append(
                {
                    "holiday": row.holiday,
                    "temp": float(row.temp),
                    "rain_1h": float(row.rain_1h),
                    "snow_1h": float(row.snow_1h),
                    "clouds_all": int(row.clouds_all),
                    "weather_main": row.weather_main,
                    "weather_description": row.weather_description,
                    "date_time": row.date_time.to_pydatetime(),
                    "traffic_volume": int(row.traffic_volume),
                }
            )

        db.execute(
            insert(TrafficRecord),
            records,
        )

        db.commit()

        print(f"Imported {len(records)} traffic records successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    import_traffic_data()