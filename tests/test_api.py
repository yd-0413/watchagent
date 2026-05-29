from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_shape():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "readings_stored" in data
    assert "events_stored" in data


def test_readings_endpoint_shape():
    response = client.get("/readings")

    assert response.status_code == 200

    data = response.json()

    assert "readings" in data
    assert isinstance(data["readings"], list)


def test_events_endpoint_shape():
    response = client.get("/events")

    assert response.status_code == 200

    data = response.json()

    assert "events" in data
    assert isinstance(data["events"], list)