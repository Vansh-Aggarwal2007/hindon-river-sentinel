"""
Dispatcher Agent:
Assigns tickets to the responsible civic/environmental department and
computes optimized patrol dispatch orders.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from app.agents.base import BaseAgent, haversine_distance_meters
from app.database import db
from app.models import Department, TicketStatus, PatrolAssignment, SeverityLevel


class DispatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Dispatcher",
            role="Routes incidents to relevant municipal/state departments and plans patrol routes"
        )

    # --- Agent Tools ---
    def tool_route_department(
        self,
        incident_type: str,
        source_hypotheses: List[Dict[str, Any]],
        severity: str
    ) -> Department:
        """
        Jurisdictional routing decision engine:
        - UPPCB: Industrial effluents, hazardous foam, chemical drain violations
        - Nagar Nigam: Municipal solid waste, riverbank garbage heaps, plastic dumping
        - UP Jal Nigam: Domestic sewer trunk lines, pumping stations, STP bypasses
        - UP Irrigation Dept: Floodplain encroachments, embankments, desiltation
        """
        # If top hypothesis indicates an industrial cluster or tannery
        if source_hypotheses:
            top_source_type = source_hypotheses[0].get("type", "")
            if top_source_type in ["industrial_cluster", "meat_processing_tannery"]:
                return Department.UPPCB

        if incident_type in ["toxic_foam", "industrial_effluent"]:
            return Department.UPPCB
        elif incident_type == "garbage_dumping":
            return Department.NAGAR_NIGAM
        elif incident_type in ["sewage_outfall", "water_anomaly"]:
            return Department.JAL_NIGAM
        elif incident_type in ["encroachment", "illegal_burning"]:
            return Department.IRRIGATION

        return Department.NAGAR_NIGAM

    def tool_plan_patrol_route(
        self,
        tickets: List[Dict[str, Any]],
        start_lat: float = 28.6692,  # Ghaziabad District Collectorate / Control Room
        start_lng: float = 77.4320
    ) -> List[Dict[str, Any]]:
        """
        Computes prioritized dispatch route using TSP Nearest-Neighbor heuristic,
        weighting CRITICAL and HIGH severity incidents first.
        """
        if not tickets:
            return []

        # Sort criteria: Severity score descending, then distance
        severity_weight = {
            SeverityLevel.CRITICAL.value: 4,
            SeverityLevel.HIGH.value: 3,
            SeverityLevel.MEDIUM.value: 2,
            SeverityLevel.LOW.value: 1
        }

        unvisited = list(tickets)
        current_lat = start_lat
        current_lng = start_lng
        current_time = datetime.now(timezone.utc)
        route = []
        step = 1

        while unvisited:
            # Score each candidate by severity and distance
            best_idx = 0
            best_score = -999999.0

            for i, cand in enumerate(unvisited):
                loc = cand.get("location", {})
                c_lat = loc.get("lat", current_lat)
                c_lng = loc.get("lng", current_lng)
                dist_km = haversine_distance_meters(current_lat, current_lng, c_lat, c_lng) / 1000.0

                s_weight = severity_weight.get(cand.get("severity", "LOW"), 1)
                # Score = higher severity minus travel distance penalty
                score = (s_weight * 10.0) - dist_km

                if score > best_score:
                    best_score = score
                    best_idx = i

            chosen = unvisited.pop(best_idx)
            c_loc = chosen.get("location", {})
            current_lat = c_loc.get("lat", current_lat)
            current_lng = c_loc.get("lng", current_lng)

            # Estimated arrival +30 minutes per stop
            eta = current_time + timedelta(minutes=30 * step)
            chosen_route_entry = {
                "route_order": step,
                "ticket_id": chosen["id"],
                "title": chosen["title"],
                "severity": chosen["severity"],
                "target_eta": eta.isoformat(),
                "location": c_loc
            }
            route.append(chosen_route_entry)
            step += 1

        return route

    def dispatch(self, ticket_id: str) -> Dict[str, Any]:
        """
        Main Agent Execution Workflow:
        1. Fetch ticket & current hypotheses
        2. Route to appropriate government agency
        3. Assign field patrol team with ETA
        4. Update ticket status to DISPATCHED
        """
        ticket = db.get_ticket(ticket_id)
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}

        inc_type = ticket.get("incident_type", "garbage_dumping")
        hypotheses = ticket.get("source_hypotheses", [])
        severity = ticket.get("severity", "MEDIUM")

        # Step 1: Route Department
        dept: Department = self.execute_tool(
            "route_department",
            incident_type=inc_type,
            source_hypotheses=hypotheses,
            severity=severity
        )

        # Step 2: Assign Officer & Patrol Unit
        patrol_roster = {
            Department.UPPCB: ("Er. R. K. Sharma (UPPCB Field Inspector)", "PATROL-UPPCB-04"),
            Department.NAGAR_NIGAM: ("Sanitation Inspector Amit Verma", "PATROL-NNG-12"),
            Department.JAL_NIGAM: ("Assistant Engineer S. K. Tyagi", "PATROL-JAL-02"),
            Department.IRRIGATION: ("Sub-Divisional Officer P. K. Singh", "PATROL-IRR-07")
        }

        officer_name, patrol_id = patrol_roster.get(
            dept,
            ("Civic Rapid Action Team", "PATROL-GEN-01")
        )

        now = datetime.now(timezone.utc)
        eta = now + timedelta(hours=2)

        assignment = PatrolAssignment(
            officer_name=officer_name,
            patrol_id=patrol_id,
            dispatched_at=now.isoformat(),
            target_eta=eta.isoformat(),
            route_order=1
        )

        # Step 3: Update ticket
        updates = {
            "assigned_department": dept.value,
            "patrol_assignment": assignment.model_dump(),
            "status": TicketStatus.DISPATCHED.value
        }
        updated_ticket = db.update_ticket(ticket_id, updates)

        self.log("PATROL_DISPATCHED", {
            "ticket_id": ticket_id,
            "department": dept.value,
            "patrol_id": patrol_id,
            "officer": officer_name
        })

        return {
            "ticket_id": ticket_id,
            "department": dept.value,
            "patrol_assignment": assignment.model_dump(),
            "ticket": updated_ticket
        }


# Singleton instance
dispatcher_agent = DispatcherAgent()
