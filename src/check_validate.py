import pandas as pd
from build_dataset import validate

# One realistic row, then deliberately broken copies
row = {"city": "Test", "timestamp": pd.Timestamp("2026-01-01"),
       "pm2_5": 10.0, "pm10": 20.0, "nitrogen_dioxide": 5.0, "ozone": 50.0,
       "us_aqi": 40, "temperature_2m": 25.0, "relative_humidity_2m": 60,
       "wind_speed_10m": 5.0, "precipitation": 0.0, "surface_pressure": 1000.0}

good = pd.DataFrame([row])
bad_humidity = pd.DataFrame([{**row, "relative_humidity_2m": 150}])   # impossible
swapped_pm = pd.DataFrame([{**row, "pm2_5": 30.0, "pm10": 20.0}])     # PM2.5 > PM10

# assert stops the script with an error if the condition is False
assert validate(good).loc[0, "is_valid"]
assert not validate(bad_humidity).loc[0, "is_valid"]
assert validate(swapped_pm).loc[0, "is_suspect"]
print("validate() checks passed")