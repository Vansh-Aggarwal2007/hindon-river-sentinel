"""
Unit and integration tests for Briefing Agent.
"""
import pytest
from app.agents.briefing import briefing_agent
from app.database import db


@pytest.fixture(autouse=True)
def reset_database():
    db.reset()


def test_briefing_generation():
    """Verify daily executive dossier generation in English and Hindi."""
    res = briefing_agent.generate_briefing()
    assert "stats" in res
    assert "english_dossier" in res
    assert "hindi_summary" in res
    assert "हिंडन नदी" in res["hindi_summary"]
    assert "Hindon River" in res["english_dossier"]
    assert res["stats"]["total_tickets"] >= 3


def test_statutory_escalation():
    """Verify legal notice drafting under Section 33A of Water Act."""
    res = briefing_agent.escalate_and_draft_notice(
        ticket_id="TKT-HIN-001",
        officer_notes="Immediate show cause notice approved by District Magistrate."
    )
    assert res["escalation_approved"] is True
    assert "SECTION 33A, WATER ACT 1974" in res["statutory_notice"]
    
    tkt = db.get_ticket("TKT-HIN-001")
    assert tkt["escalation_approved"] is True
