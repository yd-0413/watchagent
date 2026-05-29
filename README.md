# WatchAgent: Weather Monitor & AI Assistant

WatchAgent is a Python backend service that monitors live weather across Ottawa, Toronto, and Vancouver. It polls Open-Meteo for current conditions, stores unique readings, detects notable weather events, and exposes the stored data through an HTTP API.

## Architecture

Open-Meteo API  
↓  
Weather Poller  
↓  
Deduplication Logic  
↓  
Event Detection Logic  
↓  
SQLite Database  
↓  
FastAPI HTTP API  

Endpoints:

- `/health`
- `/readings`
- `/events`

## Technology Choices

This project uses FastAPI because it is lightweight, easy to test, and provides automatic API documentation at `/docs`.

SQLite is used for storage because the challenge requires a small persistent database and SQLite works well with Docker volumes without requiring extra infrastructure.

SQLAlchemy is used to keep database models structured and to make testing easier.

APScheduler is used to run the weather poller repeatedly in the background while the API server is running.

## Monitored Cities

The service monitors:

- Ottawa, Canada: lat `45.42`, lon `-75.69`
- Toronto, Canada: lat `43.70`, lon `-79.42`
- Vancouver, Canada: lat `49.25`, lon `-123.12`

## Data Source

Weather data comes from Open-Meteo:

`https://api.open-meteo.com/v1/forecast`

The service stores these current weather fields:

- `temperature_2m`
- `apparent_temperature`
- `precipitation`
- `wind_speed_10m`
- `weather_code`

## Deduplication

Open-Meteo updates current readings hourly. Since this service polls more frequently than once per hour, the same reading can appear multiple times.

To avoid duplicates, WatchAgent only stores a reading when the city and timestamp combination is new.

Unique reading rule:

`city + timestamp`

## Event Detection Logic

The service detects notable events when weather data is useful enough to surface to a reviewer.

### 1. Sudden Temperature Change

An event fires when the temperature changes by at least `5°C` compared to the previous stored reading for the same city.

Reasoning: a fast temperature shift can matter more than a single temperature value by itself.

### 2. Heavy Precipitation

An event fires when precipitation is at least `2.5 mm` in the previous hour.

Reasoning: precipitation behaves differently from temperature. A single hour of noticeable rain can affect travel and outdoor plans.

### 3. Strong Wind

An event fires when wind speed reaches at least `40 km/h`.

Reasoning: strong wind can affect driving, walking, outdoor work, and general safety.

### 4. Cross-City Temperature Anomaly

An event fires when a city is at least `8°C` warmer or colder than the average of the other monitored cities.

Reasoning: this captures regional contrast instead of only looking at one city in isolation.

## API Reference

### GET `/health`

Returns service status and stored record counts.

Example:

`curl http://localhost:8000/health`

Example response:

`{"status":"ok","readings_stored":3,"events_stored":0}`

### GET `/readings`

Returns stored weather readings, most recent first.

Optional query parameters:

- `city`
- `limit`

Example:

`curl "http://localhost:8000/readings?city=Ottawa&limit=50"`

### GET `/events`

Returns stored notable weather events, most recent first.

Optional query parameters:

- `city`
- `limit`

Example:

`curl "http://localhost:8000/events?city=Ottawa&limit=50"`

## Running Locally

Create a virtual environment:

`python -m venv venv`

Activate it on Windows:

`.\venv\Scripts\Activate.ps1`

Install dependencies:

`pip install -r requirements.txt`

Create the local environment file:

`Copy-Item .env.example .env`

Run the API:

`uvicorn app.main:app --reload`

The API will be available at:

`http://localhost:8000`

FastAPI docs are available at:

`http://localhost:8000/docs`

## Running with Docker

From a clean clone:

`git clone <your-repo-url>`

`cd watchagent`

`cp .env.example .env`

`docker compose up --build`

On Windows PowerShell:

`Copy-Item .env.example .env`

`docker compose up --build`

The API will be reachable at:

`http://localhost:8000`

The SQLite database persists through the Docker volume defined in `docker-compose.yml`.

## Environment Variables

See `.env.example`.

- `DATABASE_URL=sqlite:///data/watchagent.db`
- `POLL_INTERVAL_SECONDS=300`

No credentials or API keys are required.

## Running Tests

Run:

`python -m pytest`

The tests cover:

- deduplication
- event detection logic
- API response shape

Weather API calls are not required for the unit tests.

## Cursor Setup

The `.cursor/` folder is committed because Cursor setup is part of the evaluation.

### Rules

`polling.mdc` defines rules for polling, failed API calls, deduplication, and safe database writes.

`event_records.mdc` defines rules for event record structure, event reasoning, and required tests for new event types.

### Agent

`event-reviewer.md` defines a custom reviewer agent for the weather event detection logic. It checks whether event thresholds are clear, whether logic is too noisy or too strict, whether duplicate events could happen, and whether tests match the stated event design.

### Skill

`analyze_weather_data.py` is an executable data analysis script. It queries the SQLite database and returns a structured JSON summary including:

- readings by city
- average temperature by city
- highest wind speed
- events by city
- events by type

Run it with:

`python .cursor/skills/analyze_weather_data.py`

## Submission Checklist

- FastAPI service works
- `/health` works
- `/readings` works
- `/events` works
- readings are deduplicated by city + timestamp
- event detection logic is implemented
- unit tests pass
- Dockerfile exists
- docker-compose.yml exists
- GitHub Actions CI exists
- `.cursor` folder is committed
- README explains architecture and decisions