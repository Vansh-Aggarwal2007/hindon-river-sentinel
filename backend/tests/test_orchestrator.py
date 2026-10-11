"""
Unit and integration tests for System Orchestrator and Replay Scenarios.
"""
import pytest
from app.agents.orchestrator import orchestrator
from app.database import db


@pytest.fixture(autouse=True)
def reset_database():
    db.reset()


def test_end_to_end_citizen_report_pipeline():
    """Verify full autonomous chain: Report -> Triage -> Source Investigator -> Dispatcher."""
    res = orchestrator.run_end_to_end_citizen_report(
        lat=28.6650,
        lng=77.4170,
        description="Severe chemical discharge and foam bubbling at the river weir.",
        image_url="https://example.com/foam.jpg"
    )
    assert res["status"] == "DISPATCHED"
    assert "ticket_id" in res
    assert "investigation" in res
    assert "dispatch" in res

    current = res["current_ticket"]
    assert current["assigned_department"] is not None
    assert len(current["source_hypotheses"]) > 0


def test_demo_replay_scenario_steps():
    """Verify scripted replay scenario steps 1 through 5."""
    # Step 1: Chemical spike detected
    s1 = orchestrator.run_demo_step("chemical_spike", 1)
    assert s1["agent"] == "Water Sentinel"

    # Step 2: Source investigation
    s2 = orchestrator.run_demo_step("chemical_spike", 2)
    assert s2["agent"] == "Source Investigator"

    # Step 3: Dispatcher
    s3 = orchestrator.run_demo_step("chemical_spike", 3)
    assert s3["agent"] == "Dispatcher"

    # Step 4: Verifier
    s4 = orchestrator.run_demo_step("chemical_spike", 4)
    assert s4["agent"] == "Verifier"

    # Step 5: Executive Briefing
    s5 = orchestrator.run_demo_step("chemical_spike", 5)
    assert s5["agent"] == "Briefing Agent"
