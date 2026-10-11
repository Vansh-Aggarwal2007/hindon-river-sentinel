"""
Unit and integration tests for Dispatcher Agent.
"""
import pytest
from app.agents.dispatcher import dispatcher_agent
from app.database import db
from app.models import Department, TicketStatus


@pytest.fixture(autouse=True)
def reset_database():
    db.reset()


def test_department_routing_logic():
    """Verify correct departmental jurisdictional assignments."""
    # Industrial foam -> UPPCB
    dept1 = dispatcher_agent.tool_route_department(
        incident_type="toxic_foam",
        source_hypotheses=[{"type": "industrial_cluster"}],
        severity="CRITICAL"
    )
    assert dept1 == Department.UPPCB

    # Garbage dumping -> Nagar Nigam Ghaziabad
    dept2 = dispatcher_agent.tool_route_department(
        incident_type="garbage_dumping",
        source_hypotheses=[],
        severity="HIGH"
    )
    assert dept2 == Department.NAGAR_NIGAM

    # Encroachment -> Irrigation Department
    dept3 = dispatcher_agent.tool_route_department(
        incident_type="encroachment",
        source_hypotheses=[],
        severity="MEDIUM"
    )
    assert dept3 == Department.IRRIGATION


def test_dispatch_ticket():
    """Verify dispatch assigns patrol unit, ETA, and updates status."""
    res = dispatcher_agent.dispatch("TKT-HIN-003")
    assert res["ticket_id"] == "TKT-HIN-003"
    assert res["ticket"]["status"] == TicketStatus.DISPATCHED.value
    assert "patrol_assignment" in res
    assert res["patrol_assignment"]["officer_name"] is not None


def test_patrol_route_optimization():
    """Verify patrol route optimization orders tickets by priority and proximity."""
    tickets = db.get_all_tickets()
    route = dispatcher_agent.tool_plan_patrol_route(tickets)
    assert len(route) == len(tickets)
    assert route[0]["route_order"] == 1
    assert "target_eta" in route[0]
