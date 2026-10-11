"""
Unit and integration tests for Verifier Agent.
"""
import pytest
from app.agents.verifier import verifier_agent
from app.database import db
from app.models import TicketStatus


@pytest.fixture(autouse=True)
def reset_database():
    db.reset()


def test_verifier_successful_remediation():
    """Verify ticket is closed when after-photo shows clean riverbank and high cleanliness score."""
    res = verifier_agent.verify(
        ticket_id="TKT-HIN-002",
        after_image_url="https://images.unsplash.com/photo-1542601906990-b4d3fb778b09",
        after_description="Embankment waste fully cleared by earthmovers and carted away to processing plant.",
        force_pass=True
    )
    assert res["verified"] is True
    assert res["status"] == TicketStatus.VERIFIED_CLOSED.value
    assert res["verification"]["after_cleanliness"] >= 80.0
    
    # Check ticket state in database
    tkt = db.get_ticket("TKT-HIN-002")
    assert tkt["status"] == TicketStatus.VERIFIED_CLOSED.value


def test_verifier_rejection_and_reopen():
    """Verify ticket is REOPENED if remediation is incomplete or dirty."""
    res = verifier_agent.verify(
        ticket_id="TKT-HIN-002",
        after_image_url="https://images.unsplash.com/photo-dirty.jpg",
        after_description="Partial cleanup attempted. Still dirty, heavy plastic leftovers along the bank.",
        force_pass=False
    )
    assert res["verified"] is False
    assert res["status"] == TicketStatus.REOPENED.value
    assert len(res["verification"]["rejection_reasons"]) > 0

    tkt = db.get_ticket("TKT-HIN-002")
    assert tkt["status"] == TicketStatus.REOPENED.value
