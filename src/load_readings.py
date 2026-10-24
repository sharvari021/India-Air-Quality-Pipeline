import pandas as pd
from psycopg2.extras import execute_values

from build_dataset import build_all, validate
from cities import CITIES
from db import get_connection

# Column order must match the order of values in each row we send
COLUMNS = [
    "city_id", "observed_at", "pm2_5", "pm10", "nitrogen_dioxide", "ozone",
    "us_aqi", "temperature_2m", "relative_humidity_2m", "wind_speed_10m",
    "precipitation", "surface_pressure", "is_valid", "is_suspect",
]

# On conflict, refresh every column except the key columns
UPDATE_COLS = [c for c in COLUMNS if c not in ("city_id", "observed_at")]

UPSERT_SQL = f"""
    INSERT INTO readings ({", ".join(COLUMNS)})
    VALUES %s
    ON CONFLICT (city_id, observed_at) DO UPDATE SET
        {", ".join(f"{c} = EXCLUDED.{c}" for c in UPDATE_COLS)},
        ingested_at = now()
"""


def load_readings(df: pd.DataFrame, conn) -> None:
    """Upsert a validated DataFrame into the readings table."""
    df = df.copy()

    # 1. Replace city names with city_id values from the cities table
    with conn.cursor() as cur:
        cur.execute("SELECT name, city_id FROM cities")
        name_to_id = dict(cur.fetchall())
    df["city_id"] = df["city"].map(name_to_id)
    if df["city_id"].isna().any():
        raise ValueError("Some cities are missing from the cities table")

    # 2. Our timestamps are naive IST. Attach the timezone so Postgres
    #    stores the exact moment (TIMESTAMPTZ). India has no daylight
    #    saving, so there are no ambiguous hours.
    df["observed_at"] = df["timestamp"].dt.tz_localize("Asia/Kolkata")

    # 3. Convert to plain Python objects. numpy types (int64, float64) can
    #    make psycopg2 fail, and NaN must become None so Postgres stores NULL.
    df = df[COLUMNS].astype(object).where(df[COLUMNS].notna(), None)
    rows = list(df.itertuples(index=False, name=None))

    # 4. One batched upsert for all rows
    with conn.cursor() as cur:
        execute_values(cur, UPSERT_SQL, rows)


if __name__ == "__main__":
    df, failures = build_all(CITIES)
    df = validate(df)

    conn = get_connection()
    try:
        load_readings(df, conn)
        conn.commit()  # nothing is permanent until commit
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM readings")
            print("Rows in readings:", cur.fetchone()[0])
        print("Failed cities:", failures)
    except Exception:
        conn.rollback()  # undo everything if any step failed
        raise
    finally:
        conn.close()