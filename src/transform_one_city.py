import pandas as pd

# Reuse the functions from Step 1. This works because fetch_one_city.py
# has the `if __name__ == "__main__"` guard, so importing it doesn't
# trigger the printing block.
from fetch_one_city import CITY, fetch_air_quality, fetch_weather


def to_dataframe(api_response: dict) -> pd.DataFrame:
    """Turn the API's 'hourly' parallel arrays into a table, one row per hour."""
    df = pd.DataFrame(api_response["hourly"])
    # "time" arrives as text like "2026-10-07T00:00". Convert it to a real
    # datetime so we can sort, filter and join on it properly.
    df["time"] = pd.to_datetime(df["time"])
    return df


def build_city_dataset(city: dict) -> pd.DataFrame:
    """Fetch air + weather for one city and return one merged hourly table."""
    air = to_dataframe(fetch_air_quality(city["lat"], city["lon"]))
    weather = to_dataframe(fetch_weather(city["lat"], city["lon"]))

    # Inner join on time, like SQL: air INNER JOIN weather USING (time).
    # validate="one_to_one" makes pandas raise an error if either table has
    # duplicate timestamps, which would silently multiply rows.
    merged = air.merge(weather, on="time", how="inner", validate="one_to_one")

    merged = merged.rename(columns={"time": "timestamp"})
    merged.insert(0, "city", city["name"])  # add a city column at the front

    # Drop hours that haven't happened yet (they're forecasts, not readings).
    # We build "now" in IST, then remove the timezone so it can be compared
    # with our timezone-naive timestamps.
    now_ist = pd.Timestamp.now(tz="Asia/Kolkata").tz_localize(None)
    merged = merged[merged["timestamp"] <= now_ist]

    return merged.reset_index(drop=True)


if __name__ == "__main__":
    df = build_city_dataset(CITY)

    print(df.shape)                    # (rows, columns)
    print(df.dtypes, "\n")             # check timestamp is datetime64, rest are numbers
    print(df.isna().sum(), "\n")       # count missing values per column
    print(df.describe().round(1))      # min / max / mean: this is how you spot odd values
    print(df.head(3))