"""
Unit and integration tests for Source Investigator Agent.
"""
import pytest
from app.agents.source_investigator import source_investigator_agent
from app.database import db


@pytest.fixture(autouse=True)
def reset_database():
    db.reset()


def test_upstream_outfalls_tool():
    """Verify hydrological tool retrieves correct upstream drains."""
    # Location near Hindon Barrage (28.6580, 77.4190)
    outfalls = source_investigator_agent.tool_get_upstream_outfalls(
        lat=28.6580,
        lng=77.4190,
        max_distance_m=5000.0
    )
    assert len(outfalls) > 0
    drain_ids = [d["id"] for d in outfalls]
    # DRAIN-01 (Sahibabad) and DRAIN-04 (Arthala) are upstream of Hindon Barrage
    assert "DRAIN-01" in drain_ids or "DRAIN-04" in drain_ids


def test_investigate_barrage_incident():
    """Verify source investigator identifies Sahibabad drain for toxic foam incident."""
    # Use initial ticket TKT-HIN-001 at Barrage
    res = source_investigator_agent.investigate("TKT-HIN-001")
    assert "top_hypotheses" in res
    top_hypotheses = res["top_hypotheses"]
    assert len(top_hypotheses) > 0
    
    top = top_hypotheses[0]
    assert "Sahibabad" in top["name"] or "DRAIN-01" in top["drain_id"]
    assert top["confidence"] >= 0.70
    assert len(top["evidence"]) >= 2
