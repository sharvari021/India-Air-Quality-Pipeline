SELECT
    c.name,
    r.observed_at,
    r.pm2_5,
    -- Window function: for each row, average the current row and the
    -- 23 rows before it, separately for each city (PARTITION BY).
    ROUND(AVG(r.pm2_5) OVER (
        PARTITION BY r.city_id
        ORDER BY r.observed_at
        ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
    )::numeric, 1) AS pm25_24h_avg
FROM readings r
JOIN cities c ON c.city_id = r.city_id
WHERE c.name = 'Delhi' AND r.is_valid
ORDER BY r.observed_at;

SELECT
    -- RANK() numbers the cities from most to least polluted. Ties share a rank.
    RANK() OVER (ORDER BY AVG(r.pm2_5) DESC) AS pm25_rank,
    c.name,
    ROUND(AVG(r.pm2_5)::numeric, 1) AS avg_pm25,
    ROUND(MAX(r.pm2_5)::numeric, 1) AS max_pm25
FROM readings r
JOIN cities c ON c.city_id = r.city_id
WHERE r.is_valid          -- exclude rows our validator marked as impossible
GROUP BY c.name
ORDER BY pm25_rank;

-- Query 3: per-city correlation between PM2.5 and weather variables.
-- Computed per city, not pooled, so differences between cities
-- don't get mixed up with weather effects.
SELECT
    c.name,
    ROUND(CORR(r.pm2_5, r.wind_speed_10m)::numeric, 2)        AS corr_wind,
    ROUND(CORR(r.pm2_5, r.relative_humidity_2m)::numeric, 2)  AS corr_humidity,
    ROUND(CORR(r.pm2_5, r.temperature_2m)::numeric, 2)        AS corr_temp
FROM readings r
JOIN cities c ON c.city_id = r.city_id
WHERE r.is_valid
GROUP BY c.name
ORDER BY corr_wind;