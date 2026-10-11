import json
import requests

# --- Configuration -----------------------------------------------------
# Keep URLs and city data at the top so they're easy to change later.
# (In Step 2 the city dict becomes a list of 15-20 cities.)
CITY = {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777}

AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_air_quality(lat: float, lon: float) -> dict:
    """Request hourly pollutant data for one location."""
    params = {
        "latitude": lat,
        "longitude": lon,
        # Comma-separated list of the variables we want back
        "hourly": "pm2_5,pm10,nitrogen_dioxide,ozone,us_aqi",
        "past_days": 3,          # include the last 3 days of data
        "forecast_days": 1,      # plus today
        "timezone": "Asia/Kolkata",  # default is GMT, so set IST explicitly
    }
    # timeout stops your script hanging forever if the server doesn't respond
    response = requests.get(AIR_URL, params=params, timeout=30)
    # Turns HTTP errors (400, 500...) into Python exceptions instead of
    # silently returning a broken response
    response.raise_for_status()
    return response.json()


def fetch_weather(lat: float, lon: float) -> dict:
    """Request hourly weather data for one location."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,"
                  "precipitation,surface_pressure",
        "past_days": 3,
        "forecast_days": 1,
        "timezone": "Asia/Kolkata",
    }
    response = requests.get(WEATHER_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    air = fetch_air_quality(CITY["lat"], CITY["lon"])
    weather = fetch_weather(CITY["lat"], CITY["lon"])

    # json.dumps with indent makes the raw JSON readable
    print("=== AIR QUALITY (raw) ===")
    print(json.dumps(air, indent=2))
    print("\n=== WEATHER (raw) ===")
    print(json.dumps(weather, indent=2))

    # Quick sanity check: the arrays inside "hourly" must all be equal length
    print("\nAir rows:", len(air["hourly"]["time"]))
    print("Weather rows:", len(weather["hourly"]["time"]))