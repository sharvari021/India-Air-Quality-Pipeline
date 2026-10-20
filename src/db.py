import os
import psycopg2
from dotenv import load_dotenv

# Reads the .env file and puts its values into environment variables
load_dotenv()


def get_connection():
    """Open a connection to the iaq database using credentials from .env."""
    # Keyword arguments (not a URL string), so passwords containing
    # special characters like @ or # don't break anything.
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "iaq"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )


if __name__ == "__main__":
    # Quick connection test: ask the server for its version
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            print(cur.fetchone()[0])
    finally:
        conn.close()  # always release the connection, even if the query fails