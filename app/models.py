from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False, index=True)
    timestamp = Column(String, nullable=False, index=True)

    temperature_2m = Column(Float, nullable=False)
    apparent_temperature = Column(Float, nullable=False)
    precipitation = Column(Float, nullable=False)
    wind_speed_10m = Column(Float, nullable=False)
    weather_code = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    events = relationship("Event", back_populates="reading")

    __table_args__ = (
        UniqueConstraint("city", "timestamp", name="unique_city_timestamp"),
    )


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False, index=True)
    timestamp = Column(String, nullable=False, index=True)

    event_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    reason = Column(String, nullable=False)

    reading_id = Column(Integer, ForeignKey("readings.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    reading = relationship("Reading", back_populates="events")

    __table_args__ = (
        UniqueConstraint("city", "timestamp", "event_type", name="unique_city_timestamp_event"),
    )