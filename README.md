# WatchAgent: Weather Monitor & AI Assistant

WatchAgent is a Python backend service that monitors live weather across Ottawa, Toronto, and Vancouver. It polls Open-Meteo for current conditions, stores unique readings, detects notable weather events, and exposes the stored data through an HTTP API.

## Architecture

```txt
Open-Meteo API
      |
      v
Weather Poller
      |
      v
Deduplication Logic
      |
      v
Event Detection Logic
      |
      v
SQLite Database
      |
      v
FastAPI HTTP API
  /health
  /readings
  /events

## Monitored Cities

The service monitors:

```txt
Ottawa, Canada     lat=45.42, lon=-75.69
Toronto, Canada    lat=43.70, lon=-79.42
Vancouver, Canada  lat=49.25, lon=-123.12

## Event Detection Logic

The service detects notable events when weather data is useful enough to surface to a reviewer.

### 1. Sudden Temperature Change

An event fires when the temperature changes by at least 5°C compared to the previous stored reading for the same city.

Reasoning: a fast temperature shift can matter more than a single temperature value by itself.

### 2. Heavy Precipitation

An event fires when precipitation is at least 2.5 mm in the previous hour.

Reasoning: precipitation behaves differently from temperature. A single hour of noticeable rain can affect travel and outdoor plans.

### 3. Strong Wind

An event fires when wind speed reaches at least 40 km/h.

Reasoning: strong wind can affect driving, walking, outdoor work, and general safety.

### 4. Cross-City Temperature Anomaly

An event fires when a city is at least 8°C warmer or colder than the average of the other monitored cities.

Reasoning: this captures regional contrast instead of only looking at one city in isolation.

## API Reference

### GET `/health`

Returns service status and stored record counts.

Example:

```bash
curl http://localhost:8000/health

## Running Locally

Create a virtual environment:

```bash
python -m venv venv

## Running with Docker

From a clean clone:

```bash
git clone <your-repo-url>
cd watchagent
cp .env.example .env
docker compose up --build

## Cursor Setup

The `.cursor/` folder is committed because Cursor setup is part of the evaluation.

### Rules

`polling.mdc` defines rules for polling, failed API calls, deduplication, and safe database writes.

`event_records.mdc` defines rules for event record structure, event reasoning, and required tests for new event types.

### Agent

`event-reviewer.md` defines a custom reviewer agent for the weather event detection logic. It checks whether event thresholds are clear, whether logic is too noisy or too strict, whether duplicate events could happen, and whether tests match the stated event design.

### Skill

`analyze_weather_data.py` is an executable data analysis script. It queries the SQLite database and returns a structured JSON summary including:

```txt
readings by city
average temperature by city
highest wind speed
events by city
events by type