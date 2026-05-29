from app.models import Reading
from app.poller import store_reading


def test_duplicate_reading_is_not_stored(db_session):
    reading_data = {
        "city": "Ottawa",
        "timestamp": "2026-05-29T10:00",
        "temperature_2m": 20.0,
        "apparent_temperature": 19.0,
        "precipitation": 0.0,
        "wind_speed_10m": 10.0,
        "weather_code": 0,
    }

    first = store_reading(db_session, reading_data)
    second = store_reading(db_session, reading_data)

    count = db_session.query(Reading).count()

    assert first is not None
    assert second is None
    assert count == 1