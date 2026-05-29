import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import CITIES
from app.event_detector import detect_events
from app.models import Event, Reading
from app.weather_client import fetch_current_weather

logger = logging.getLogger(__name__)


def get_previous_reading(db: Session, city: str, timestamp: str) -> Reading | None:
    return (
        db.query(Reading)
        .filter(Reading.city == city, Reading.timestamp != timestamp)
        .order_by(Reading.timestamp.desc())
        .first()
    )


def get_city_average_temperature(db: Session, current_city: str) -> float | None:
    latest_readings = []

    for city in CITIES:
        if city == current_city:
            continue

        reading = (
            db.query(Reading)
            .filter(Reading.city == city)
            .order_by(Reading.timestamp.desc())
            .first()
        )

        if reading:
            latest_readings.append(reading.temperature_2m)

    if not latest_readings:
        return None

    return sum(latest_readings) / len(latest_readings)


def store_reading(db: Session, reading_data: dict) -> Reading | None:
    existing = (
        db.query(Reading)
        .filter(
            Reading.city == reading_data["city"],
            Reading.timestamp == reading_data["timestamp"],
        )
        .first()
    )

    if existing:
        logger.info("Duplicate reading skipped for %s at %s", reading_data["city"], reading_data["timestamp"])
        return None

    reading = Reading(**reading_data)
    db.add(reading)

    try:
        db.commit()
        db.refresh(reading)
        return reading
    except IntegrityError:
        db.rollback()
        logger.info("Duplicate reading skipped after integrity check.")
        return None


def store_events(db: Session, events: list[dict]) -> int:
    stored_count = 0

    for event_data in events:
        event = Event(**event_data)
        db.add(event)

        try:
            db.commit()
            stored_count += 1
        except IntegrityError:
            db.rollback()
            logger.info(
                "Duplicate event skipped for %s at %s",
                event_data["city"],
                event_data["timestamp"],
            )

    return stored_count


def poll_once(db: Session) -> dict:
    readings_stored = 0
    events_stored = 0
    errors = []

    for city in CITIES:
        try:
            reading_data = fetch_current_weather(city)
            reading = store_reading(db, reading_data)

            if not reading:
                continue

            readings_stored += 1

            previous_reading = get_previous_reading(db, reading.city, reading.timestamp)
            city_average_temp = get_city_average_temperature(db, reading.city)

            events = detect_events(reading, previous_reading, city_average_temp)
            events_stored += store_events(db, events)

        except Exception as error:
            logger.warning("Polling failed for %s: %s", city, error)
            errors.append({"city": city, "error": str(error)})

    return {
        "readings_stored": readings_stored,
        "events_stored": events_stored,
        "errors": errors,
    }