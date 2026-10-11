"""
Integration tests for FastAPI REST API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    db.reset()


def test_health_check_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert len(data["agents_active"]) == 7


def test_get_tickets_endpoint():
    res = client.get("/api/tickets")
    assert res.status_code == 200
    tickets = res.json()
    assert len(tickets) >= 3


def test_post_report_endpoint():
    res = client.post("/api/tickets", json={
        "lat": 28.6940,
        "lng": 77.4080,
        "description": "Black sewage sludge spilling from outfall",
        "title": "Karhera Blackwater Outfall"
    })
    assert res.status_code == 200
    data = res.json()
    assert "ticket" in data or "existing_ticket_id" in data


def test_sensors_endpoint():
    res = client.get("/api/sensors")
    assert res.status_code == 200
    sensors = res.json()
    assert len(sensors) == 4


def test_drains_endpoint():
    res = client.get("/api/drains")
    assert res.status_code == 200
    drains = res.json()
    assert len(drains) == 6


def test_briefing_endpoint():
    res = client.get("/api/briefing")
    assert res.status_code == 200
    data = res.json()
    assert "english_dossier" in data
    assert "hindi_summary" in data


def test_demo_step_endpoint():
    res = client.post("/api/demo/step", json={
        "scenario_id": "chemical_spike",
        "step_index": 1
    })
    assert res.status_code == 200
    data = res.json()
    assert data["agent"] == "Water Sentinel"
