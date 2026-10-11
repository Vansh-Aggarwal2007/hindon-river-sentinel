"""
Unit and integration tests for Water Sentinel Agent.
"""
import pytest
from app.agents.water_sentinel import water_sentinel_agent
from app.database import db
from app.models import SeverityLevel


@pytest.fixture(autouse=True)
def reset_database():
    db.reset()


def test_water_sentinel_normal_reading():
    """Verify normal readings do not trigger anomalies."""
    water_sentinel_agent.set_rainfall(0.0)
    normal_data = {
        "ph": 7.4,
        "turbidity_ntu": 38.0,
        "tds_ppm": 550.0,
        "temp_c": 25.5,
        "lat": 28.6940,
        "lng": 77.4080
    }
    result = water_sentinel_agent.process_sensor_node("HIN-NODE-01", normal_data)
    assert result["status"] == "NORMAL"
    assert not result["eval"]["is_anomaly"]


def test_water_sentinel_chemical_spike_alert():
    """Verify acidic pH and high TDS trigger confirmed anomaly alert."""
    water_sentinel_agent.set_rainfall(0.0)  # Dry weather
    spike_data = {
        "ph": 5.1,
        "turbidity_ntu": 180.0,
        "tds_ppm": 2300.0,
        "temp_c": 28.0,
        "lat": 28.6585,
        "lng": 77.4185,
        "node_name": "Hindon Barrage Central Sensor"
    }
    result = water_sentinel_agent.process_sensor_node("HIN-NODE-02", spike_data)
    assert result["status"] == "ANOMALY_CONFIRMED"
    assert "ticket" in result
    ticket = result["ticket"]
    assert ticket["severity"] == SeverityLevel.CRITICAL.value
    assert "Chemical Spike" in ticket["title"]


def test_water_sentinel_rainfall_false_alarm_filter():
    """Verify rainfall filter ignores silt turbidity during heavy storms."""
    water_sentinel_agent.set_rainfall(25.0)  # 25mm rain
    storm_data = {
        "ph": 7.2,               # Normal neutral
        "turbidity_ntu": 190.0,  # High turbidity from rainwater runoff
        "tds_ppm": 610.0,        # Diluted TDS
        "temp_c": 23.0,
        "lat": 28.6940,
        "lng": 77.4080
    }
    result = water_sentinel_agent.process_sensor_node("HIN-NODE-01", storm_data)
    assert result["status"] == "RAIN_FILTERED"
    assert "False alarm filtered" in result["reason"] or "precipitation" in result["reason"]
