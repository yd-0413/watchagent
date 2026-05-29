import logging

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from app.config import POLL_INTERVAL_SECONDS
from app.database import Base, SessionLocal, engine, get_db
from app.models import Event, Reading
from app.poller import poll_once
from app.schemas import EventResponse, ReadingResponse

logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="WatchAgent Weather Monitor")

scheduler = BackgroundScheduler()


def scheduled_poll():
    db = SessionLocal()
    try:
        poll_once(db)
    finally:
        db.close()


@app.on_event("startup")
def start_poller():
    scheduled_poll()
    scheduler.add_job(scheduled_poll, "interval", seconds=POLL_INTERVAL_SECONDS)
    scheduler.start()


@app.on_event("shutdown")
def stop_poller():
    scheduler.shutdown()


@app.get("/health")
def health(db: Session = Depends(get_db)):
    readings_stored = db.query(Reading).count()
    events_stored = db.query(Event).count()

    return {
        "status": "ok",
        "readings_stored": readings_stored,
        "events_stored": events_stored,
    }


@app.get("/readings")
def get_readings(
    city: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Reading)

    if city:
        query = query.filter(Reading.city == city)

    readings = query.order_by(Reading.timestamp.desc()).limit(limit).all()

    return {
        "readings": [ReadingResponse.model_validate(reading) for reading in readings]
    }


@app.get("/events")
def get_events(
    city: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Event)

    if city:
        query = query.filter(Event.city == city)

    events = query.order_by(Event.timestamp.desc()).limit(limit).all()

    return {
        "events": [EventResponse.model_validate(event) for event in events]
    }