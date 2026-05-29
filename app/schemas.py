from datetime import datetime
from pydantic import BaseModel


class ReadingResponse(BaseModel):
    id: int
    city: str
    timestamp: str
    temperature_2m: float
    apparent_temperature: float
    precipitation: float
    wind_speed_10m: float
    weather_code: int
    created_at: datetime

    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    id: int
    city: str
    timestamp: str
    event_type: str
    severity: str
    summary: str
    reason: str
    reading_id: int
    created_at: datetime

    class Config:
        from_attributes = True