"""
Unit and integration tests for Triage Agent.
"""
import pytest
from app.agents.triage import triage_agent
from app.database import db
from app.models import IncidentType, SeverityLevel, TicketStatus


@pytest.fixture(autouse=True)
def reset_database():
    db.reset()


def test_triage_toxic_foam_classification():
    """Verify triage agent detects toxic foam and assigns high severity."""
    result = triage_agent.process_report(
        lat=28.6650,
        lng=77.4170,
        description="Massive white toxic foam and chemical froth floating over the weir near GT Road bridge.",
        image_url="https://example.com/foam.jpg"
    )
    assert not result["is_duplicate"]
    ticket = result["ticket"]
    assert ticket["incident_type"] == IncidentType.TOXIC_FOAM.value
    assert ticket["severity"] == SeverityLevel.CRITICAL.value
    assert ticket["status"] == TicketStatus.OPEN.value
    assert any("foam" in obj or "froth" in obj for obj in ticket["before_photo_analysis"]["detected_objects"])


def test_triage_garbage_dumping_classification():
    """Verify triage agent detects municipal plastic garbage dumping."""
    result = triage_agent.process_report(
        lat=28.6800,
        lng=77.4100,
        description="Commercial trucks dumping plastic bags and food market garbage on the embankment.",
        image_url="https://example.com/garbage.jpg"
    )
    assert not result["is_duplicate"]
    ticket = result["ticket"]
    assert ticket["incident_type"] == IncidentType.GARBAGE_DUMPING.value
    assert ticket["severity"] in [SeverityLevel.HIGH.value, SeverityLevel.MEDIUM.value]


def test_triage_duplicate_detection():
    """Verify triage agent detects reports in close proximity (<200m) to active incidents."""
    # First report
    rep1 = triage_agent.process_report(
        lat=28.6750,
        lng=77.4150,
        description="Open burning of plastic waste on riverbank."
    )
    assert not rep1["is_duplicate"]
    ticket_id = rep1["ticket"]["id"]

    # Second report 50 meters away
    rep2 = triage_agent.process_report(
        lat=28.6753,  # ~30 meters away
        lng=77.4152,
        description="Black smoke and burning trash at the same river spot."
    )
    assert rep2["is_duplicate"]
    assert rep2["existing_ticket_id"] == ticket_id
