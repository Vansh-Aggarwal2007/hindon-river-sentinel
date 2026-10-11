"""
Source Investigator Agent:
The core agentic reasoning engine. When a water pollution spike or dumping ticket is raised,
this agent backtracks along the hydrological gradient (upstream flow), queries GIS drain outfalls,
evaluates chemical signatures against industrial catchments, and produces ranked source hypotheses.
"""
from typing import Dict, Any, List, Optional
from app.agents.base import BaseAgent, haversine_distance_meters
from app.database import db
from app.models import SourceHypothesis, TicketStatus


class SourceInvestigatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Source Investigator",
            role="Multi-step hydrological backtracking and GIS outfall correlation to identify pollution sources"
        )

    # --- Agent Tools ---
    def tool_get_upstream_outfalls(self, lat: float, lng: float, max_distance_m: float = 6000.0) -> List[Dict[str, Any]]:
        """
        Hydrological GIS tool:
        The Hindon flows North to South in Ghaziabad. Upstream drains have higher latitude
        (or are within proximal upstream meander reach).
        """
        all_drains = db.get_all_drains()
        upstream_candidates = []

        for d in all_drains:
            d_lat = d["lat"]
            d_lng = d["lng"]
            dist_m = haversine_distance_meters(lat, lng, d_lat, d_lng)

            # Upstream test: drain latitude is north of the incident (lat > incident_lat - 0.005)
            # and within reachable upstream distance
            if d_lat >= (lat - 0.005) and dist_m <= max_distance_m:
                cand = dict(d)
                cand["distance_m"] = round(dist_m, 1)
                upstream_candidates.append(cand)

        # Sort closest upstream first
        upstream_candidates.sort(key=lambda x: x["distance_m"])
        return upstream_candidates

    def tool_get_land_use_and_profile(self, drain_id: str) -> Optional[Dict[str, Any]]:
        """
        Queries municipal and UPPCB GIS database for industrial zoning,
        drain discharge permit records, and chemical profiles.
        """
        return db.get_drain(drain_id)

    def tool_evaluate_chemical_match(
        self,
        incident_type: str,
        drain_profile: Dict[str, Any],
        sensor_trigger: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Correlates observed pollution characteristics with known industrial signatures.
        """
        drain_type = drain_profile.get("type", "")
        pollutants = drain_profile.get("typical_pollutants", [])
        evidence_points = []
        match_score = 0.5  # Base

        # If sensor trigger is available (e.g. acidic pH, high TDS)
        if sensor_trigger and "parameters" in sensor_trigger:
            params = sensor_trigger["parameters"]
            ph = params.get("ph", 7.0)
            tds = params.get("tds", 500.0)

            if ph < 6.0 and "electroplating_acids" in pollutants:
                match_score += 0.35
                evidence_points.append(f"Acidic pH violation ({ph:.2f}) strongly matches industrial acid bath effluents from {drain_profile['name']}")
            
            if tds > 1800.0 and ("heavy_metals" in pollutants or "dyes" in pollutants):
                match_score += 0.30
                evidence_points.append(f"Severe TDS spike ({tds:.1f} ppm) aligns with chemical salts and dye effluents from {drain_profile['catchment_area']}")

        # Match incident types
        if incident_type in ["toxic_foam", "industrial_effluent"]:
            if "industrial_cluster" in drain_type:
                match_score += 0.3
                evidence_points.append(f"High-density surfactant surfactants documented in {drain_profile['catchment_area']}")
            elif "mixed_industrial_domestic" in drain_type:
                match_score += 0.15
                evidence_points.append("Mixed domestic detergents contribute to secondary foam formation")

        elif incident_type == "garbage_dumping":
            if "municipal" in drain_type or "solid_waste" in drain_type:
                match_score += 0.4
                evidence_points.append(f"Drain bank serves as known unauthorized municipal dumping corridor for {drain_profile['catchment_area']}")

        elif incident_type == "sewage_outfall":
            if "stp_bypass" in drain_type or "municipal_sewage" in drain_type:
                match_score += 0.45
                evidence_points.append(f"Direct untreated blackwater discharge reported at {drain_profile['name']}")

        match_score = min(0.98, max(0.2, match_score))
        return {
            "match_score": match_score,
            "evidence": evidence_points
        }

    def investigate(self, ticket_id: str) -> Dict[str, Any]:
        """
        Main Agent Execution Workflow:
        1. Fetch ticket location and incident type
        2. Execute GIS upstream tool to locate active drains
        3. For each candidate, evaluate chemical matching & land use
        4. Synthesize top ranked hypotheses and save to ticket
        """
        ticket = db.get_ticket(ticket_id)
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}

        lat = ticket["location"]["lat"]
        lng = ticket["location"]["lng"]
        inc_type = ticket.get("incident_type", "water_anomaly")
        sensor_trigger = ticket.get("sensor_trigger")

        self.log("INVESTIGATION_STARTED", {
            "ticket_id": ticket_id,
            "location": {"lat": lat, "lng": lng},
            "type": inc_type
        })

        # Step 1: Upstream GIS search
        candidates = self.execute_tool("get_upstream_outfalls", lat=lat, lng=lng, max_distance_m=5000.0)

        # Fallback if no candidate immediately upstream (take closest drain)
        if not candidates:
            all_d = db.get_all_drains()
            if all_d:
                all_d.sort(key=lambda d: haversine_distance_meters(lat, lng, d["lat"], d["lng"]))
                candidates = [dict(all_d[0], distance_m=haversine_distance_meters(lat, lng, all_d[0]["lat"], all_d[0]["lng"]))]

        # Step 2: Multi-factor evaluation
        hypotheses: List[SourceHypothesis] = []
        for cand in candidates:
            drain_id = cand["id"]
            profile = self.execute_tool("get_land_use_and_profile", drain_id=drain_id)
            if not profile:
                continue

            chem_eval = self.execute_tool(
                "evaluate_chemical_match",
                incident_type=inc_type,
                drain_profile=profile,
                sensor_trigger=sensor_trigger
            )

            # Distance decay: closer drains have higher probability
            dist_m = cand.get("distance_m", 1000.0)
            proximity_weight = max(0.1, 1.0 - (dist_m / 6000.0))
            
            # Composite confidence calculation
            confidence = round(0.6 * chem_eval["match_score"] + 0.4 * proximity_weight, 2)
            confidence = min(0.97, max(0.35, confidence))

            evidence = [
                f"Hydrological flow vector traces {dist_m:.0f}m upstream along main channel",
                f"Catchment jurisdiction: {profile.get('regulatory_jurisdiction', 'Local Authority')}",
                *chem_eval["evidence"]
            ]

            hypotheses.append(SourceHypothesis(
                source_id=f"SRC-{drain_id}",
                name=profile["name"],
                drain_id=drain_id,
                type=profile["type"],
                confidence=confidence,
                distance_upstream_m=dist_m,
                evidence=evidence
            ))

        # Sort by confidence descending
        hypotheses.sort(key=lambda h: h.confidence, reverse=True)
        top_hypotheses = hypotheses[:3]

        # Update Ticket
        updates = {
            "status": TicketStatus.INVESTIGATING.value,
            "source_hypotheses": [h.model_dump() for h in top_hypotheses]
        }
        updated_ticket = db.update_ticket(ticket_id, updates)

        self.log("INVESTIGATION_COMPLETED", {
            "ticket_id": ticket_id,
            "top_source": top_hypotheses[0].name if top_hypotheses else "None",
            "confidence": top_hypotheses[0].confidence if top_hypotheses else 0.0
        })

        return {
            "ticket_id": ticket_id,
            "top_hypotheses": [h.model_dump() for h in top_hypotheses],
            "ticket": updated_ticket
        }


# Singleton instance
source_investigator_agent = SourceInvestigatorAgent()
