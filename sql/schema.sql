-- One row per city: static metadata stored once, not repeated per reading.
CREATE TABLE IF NOT EXISTS cities (
    city_id    SERIAL PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE,
    latitude   DOUBLE PRECISION NOT NULL,
    longitude  DOUBLE PRECISION NOT NULL
);

-- One row per city per hour.
CREATE TABLE IF NOT EXISTS readings (
    city_id               INTEGER NOT NULL REFERENCES cities(city_id),
    observed_at           TIMESTAMPTZ NOT NULL,
    pm2_5                 DOUBLE PRECISION,
    pm10                  DOUBLE PRECISION,
    nitrogen_dioxide      DOUBLE PRECISION,
    ozone                 DOUBLE PRECISION,
    us_aqi                INTEGER,
    temperature_2m        DOUBLE PRECISION,
    relative_humidity_2m  INTEGER,
    wind_speed_10m        DOUBLE PRECISION,
    precipitation         DOUBLE PRECISION,
    surface_pressure      DOUBLE PRECISION,
    is_valid              BOOLEAN NOT NULL,
    is_suspect            BOOLEAN NOT NULL,
    ingested_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- The same city+hour can exist only once: this makes re-runs safe.
    PRIMARY KEY (city_id, observed_at)
);

-- The primary key speeds up "one city over time" queries. This index
-- speeds up "all cities at a given time" queries (rankings, comparisons).
CREATE INDEX IF NOT EXISTS idx_readings_observed_at ON readings (observed_at);