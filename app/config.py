import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/watchagent.db")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))

CITIES = {
    "Ottawa": {"lat": 45.42, "lon": -75.69},
    "Toronto": {"lat": 43.70, "lon": -79.42},
    "Vancouver": {"lat": 49.25, "lon": -123.12},
}