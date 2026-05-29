from app.event_detector import detect_events
from app.models import Reading


def make_reading(
    city="Ottawa",
    timestamp="2026-05-29T10:00",
    temperature_2m=20.0,
    apparent_temperature=20.0,
    precipitation=0.0,
    wind_speed_10m=10.0,
    weather_code=0,
):
    reading = Reading(
        city=city,
        timestamp=timestamp,
        temperature_2m=temperature_2m,
        apparent_temperature=apparent_temperature,
        precipitation=precipitation,
        wind_speed_10m=wind_speed_10m,
        weather_code=weather_code,
    )
    reading.id = 1
    return reading


def test_sudden_temperature_change_fires():
    previous = make_reading(temperature_2m=10.0)
    current = make_reading(timestamp="2026-05-29T11:00", temperature_2m=16.0)

    events = detect_events(current, previous)

    assert len(events) == 1
    assert events[0]["event_type"] == "sudden_temperature_change"


def test_small_temperature_change_does_not_fire():
    previous = make_reading(temperature_2m=10.0)
    current = make_reading(timestamp="2026-05-29T11:00", temperature_2m=12.0)

    events = detect_events(current, previous)

    assert events == []


def test_heavy_precipitation_fires():
    current = make_reading(precipitation=3.0)

    events = detect_events(current)

    assert len(events) == 1
    assert events[0]["event_type"] == "heavy_precipitation"


def test_strong_wind_fires():
    current = make_reading(wind_speed_10m=45.0)

    events = detect_events(current)

    assert len(events) == 1
    assert events[0]["event_type"] == "strong_wind"


def test_cross_city_temperature_anomaly_fires():
    current = make_reading(city="Ottawa", temperature_2m=25.0)

    events = detect_events(current, city_average_temp=15.0)

    assert len(events) == 1
    assert events[0]["event_type"] == "cross_city_temperature_anomaly"