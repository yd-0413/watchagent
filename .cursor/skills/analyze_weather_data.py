import json
import os
import sqlite3
from pathlib import Path


def get_database_path() -> Path:
    database_url = os.getenv("DATABASE_URL", "sqlite:///data/watchagent.db")

    if database_url.startswith("sqlite:///"):
        return Path(database_url.replace("sqlite:///", ""))

    return Path("data/watchagent.db")


def table_exists(cursor, table_name: str) -> bool:
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def main():
    db_path = get_database_path()

    if not db_path.exists():
        print(json.dumps({
            "error": f"Database not found at {str(db_path)}",
            "hint": "Run the API first so the poller can create and populate the database."
        }, indent=2))
        return

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    if not table_exists(cursor, "readings"):
        print(json.dumps({
            "error": "readings table not found",
            "hint": "Run the API first so SQLAlchemy can create the tables."
        }, indent=2))
        connection.close()
        return

    result = {}

    cursor.execute("""
        SELECT city, COUNT(*)
        FROM readings
        GROUP BY city
        ORDER BY city
    """)
    result["readings_by_city"] = dict(cursor.fetchall())

    cursor.execute("""
        SELECT city, ROUND(AVG(temperature_2m), 2)
        FROM readings
        GROUP BY city
        ORDER BY city
    """)
    result["average_temperature_by_city"] = dict(cursor.fetchall())

    cursor.execute("""
        SELECT city, wind_speed_10m, timestamp
        FROM readings
        ORDER BY wind_speed_10m DESC
        LIMIT 1
    """)
    highest_wind = cursor.fetchone()

    result["highest_wind_speed"] = None

    if highest_wind:
        result["highest_wind_speed"] = {
            "city": highest_wind[0],
            "value_kmh": highest_wind[1],
            "timestamp": highest_wind[2],
        }

    if table_exists(cursor, "events"):
        cursor.execute("""
            SELECT city, COUNT(*)
            FROM events
            GROUP BY city
            ORDER BY city
        """)
        result["events_by_city"] = dict(cursor.fetchall())

        cursor.execute("""
            SELECT event_type, COUNT(*)
            FROM events
            GROUP BY event_type
            ORDER BY event_type
        """)
        result["events_by_type"] = dict(cursor.fetchall())
    else:
        result["events_by_city"] = {}
        result["events_by_type"] = {}

    connection.close()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()