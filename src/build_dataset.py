import time
import pandas as pd
import requests

from cities import CITIES
from transform_one_city import build_city_dataset

# HARD limits: physically impossible outside these ranges, so the data is
# wrong. (Pressure lower bound is 850, not 1000, because hill cities like
# Bengaluru sit at ~900 m elevation, where surface pressure is ~910 hPa.)
HARD_LIMITS = {
    "pm2_5": (0, 1000), "pm10": (0, 2000),
    "nitrogen_dioxide": (0, 1000), "ozone": (0, 1000),
    "us_aqi": (0, 500),
    "temperature_2m": (-10, 55),
    "relative_humidity_2m": (0, 100),
    "wind_speed_10m": (0, 200),
    "precipitation": (0, 300),
    "surface_pressure": (850, 1100),
}

# SOFT ceilings: possible but suspicious. Flagged for review, not rejected.
# Placeholder values. We'll tune them after looking at describe() output.
SOFT_CEILINGS = {"ozone": 400, "pm2_5": 500, "nitrogen_dioxide": 300}


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Add is_valid / is_suspect flag columns. Never deletes rows."""
    df = df.copy()

    invalid = pd.Series(False, index=df.index)
    for col, (low, high) in HARD_LIMITS.items():
        # between() returns False for NaN, so a missing value is also
        # treated as invalid. That's what we want.
        invalid |= ~df[col].between(low, high)
    df["is_valid"] = ~invalid

    suspect = pd.Series(False, index=df.index)
    for col, ceiling in SOFT_CEILINGS.items():
        suspect |= df[col] > ceiling
    df["is_suspect"] = suspect
    return df


def build_all(cities: list) -> tuple:
    """Fetch every city. One failure must not kill the whole run."""
    frames, failures = [], []
    for city in cities:
        try:
            frames.append(build_city_dataset(city))
            print(f"ok      {city['name']}")
        except (requests.RequestException, KeyError, ValueError) as err:
            failures.append((city["name"], str(err)))
            print(f"FAILED  {city['name']}: {err}")
        time.sleep(1)  # be polite to a free API: 1 second between calls
    return pd.concat(frames, ignore_index=True), failures


if __name__ == "__main__":
    pd.set_option("display.width", 200)       # stop the "..." truncation
    pd.set_option("display.max_columns", None)

    df, failures = build_all(CITIES)
    df = validate(df)

    print("\nShape:", df.shape)
    print("\nRows per city (should all be equal):")
    print(df.groupby("city").size().to_string())
    print("\nFlag counts per city:")
    print(df.groupby("city")[["is_suspect"]].sum().to_string())
    print("\nInvalid rows:", (~df["is_valid"]).sum())
    print("Failures:", failures)

    # Transposed, so every variable is a row and nothing gets cut off
    print("\n", df.describe().T.round(1))