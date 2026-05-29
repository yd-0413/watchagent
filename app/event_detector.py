from app.models import Reading


def detect_events(current_reading: Reading, previous_reading: Reading | None = None, city_average_temp: float | None = None) -> list[dict]:
    events = []

    # 1. Sudden temperature change compared to previous reading in same city
    if previous_reading:
        temp_change = current_reading.temperature_2m - previous_reading.temperature_2m

        if abs(temp_change) >= 5:
            direction = "increased" if temp_change > 0 else "dropped"

            events.append({
                "city": current_reading.city,
                "timestamp": current_reading.timestamp,
                "event_type": "sudden_temperature_change",
                "severity": "medium",
                "summary": f"Sudden temperature change detected in {current_reading.city}",
                "reason": (
                    f"Temperature {direction} by {abs(temp_change):.1f}°C compared to the previous reading. "
                    "This passed the 5°C change threshold."
                ),
                "reading_id": current_reading.id,
            })

    # 2. Heavy precipitation
    if current_reading.precipitation >= 2.5:
        events.append({
            "city": current_reading.city,
            "timestamp": current_reading.timestamp,
            "event_type": "heavy_precipitation",
            "severity": "high" if current_reading.precipitation >= 5 else "medium",
            "summary": f"Heavy precipitation detected in {current_reading.city}",
            "reason": (
                f"Precipitation reached {current_reading.precipitation:.1f} mm in the previous hour. "
                "This passed the 2.5 mm threshold."
            ),
            "reading_id": current_reading.id,
        })

    # 3. Strong wind
    if current_reading.wind_speed_10m >= 40:
        events.append({
            "city": current_reading.city,
            "timestamp": current_reading.timestamp,
            "event_type": "strong_wind",
            "severity": "high" if current_reading.wind_speed_10m >= 60 else "medium",
            "summary": f"Strong wind detected in {current_reading.city}",
            "reason": (
                f"Wind speed reached {current_reading.wind_speed_10m:.1f} km/h. "
                "This passed the 40 km/h threshold."
            ),
            "reading_id": current_reading.id,
        })

    # 4. Cross-city temperature anomaly
    if city_average_temp is not None:
        difference = current_reading.temperature_2m - city_average_temp

        if abs(difference) >= 8:
            direction = "warmer" if difference > 0 else "colder"

            events.append({
                "city": current_reading.city,
                "timestamp": current_reading.timestamp,
                "event_type": "cross_city_temperature_anomaly",
                "severity": "medium",
                "summary": f"{current_reading.city} is unusually {direction} than the other monitored cities",
                "reason": (
                    f"{current_reading.city} was {abs(difference):.1f}°C {direction} than the average "
                    "of the other monitored cities. This passed the 8°C difference threshold."
                ),
                "reading_id": current_reading.id,
            })

    return events