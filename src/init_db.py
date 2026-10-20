from pathlib import Path

from cities import CITIES
from db import get_connection

# Locate sql/schema.sql relative to this file, so it works from any folder
SCHEMA_FILE = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"


def init_db():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Create the tables from the schema file
            cur.execute(SCHEMA_FILE.read_text(encoding="utf-8"))

            # 2. Insert the 15 cities. %s placeholders let psycopg2 pass the
            #    values separately from the SQL text, which prevents SQL
            #    injection. Never build SQL with f-strings.
            for c in CITIES:
                cur.execute(
                    """
                    INSERT INTO cities (name, latitude, longitude)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name) DO UPDATE
                    SET latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude
                    """,
                    (c["name"], c["lat"], c["lon"]),
                )
        # Nothing is permanent until commit. If anything above failed, the
        # whole transaction is rolled back and the database stays unchanged.
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM cities;")
            print("Cities in database:", cur.fetchone()[0])
    except Exception:
        conn.rollback()
        raise  # re-raise so you still see the real error
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()