"""
System Orchestrator:
Coordinates the multi-agent pipeline, passes events across agents,
and manages interactive demo replay scenarios for hackathon presentations.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.agents.base import BaseAgent
from app.agents.triage import triage_agent
from app.agents.water_sentinel import water_sentinel_agent
from app.agents.source_investigator import source_investigator_agent
from app.agents.dispatcher import dispatcher_agent
from app.agents.verifier import verifier_agent
from app.agents.briefing import briefing_agent
from app.database import db
from app.models import TicketStatus, SeverityLevel, IncidentType


class SystemOrchestrator(BaseAgent):
    def __init__(self):
        super().__init__(
            name="System Orchestrator",
            role="Central event bus and coordinator managing multi-agent pipeline transitions"
        )

    def run_end_to_end_citizen_report(
        self,
        lat: float,
        lng: float,
        description: str,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes full pipeline for a citizen report:
        1. Triage Agent (Vision & Deduplication)
        2. Source Investigator Agent (Upstream outfall analysis)
        3. Dispatcher Agent (Assigns dept & patrol team)
        """
        # Step 1: Triage
        triage_res = triage_agent.process_report(
            lat=lat,
            lng=lng,
            description=description,
            image_url=image_url
        )

        if triage_res.get("is_duplicate"):
            return {
                "step": "TRIAGE",
                "status": "DUPLICATE",
                "details": triage_res
            }

        ticket = triage_res["ticket"]
        ticket_id = ticket["id"]

        # Step 2: Source Investigation
        invest_res = source_investigator_agent.investigate(ticket_id)

        # Step 3: Dispatcher
        dispatch_res = dispatcher_agent.dispatch(ticket_id)

        self.log("PIPELINE_EXECUTED", {
            "ticket_id": ticket_id,
            "flow": "CitizenReport -> Triage -> SourceInvestigator -> Dispatcher"
        })

        return {
            "status": "DISPATCHED",
            "ticket_id": ticket_id,
            "triage": triage_res,
            "investigation": invest_res,
            "dispatch": dispatch_res,
            "current_ticket": db.get_ticket(ticket_id)
        }

    def run_sensor_spike_pipeline(self, node_id: str, reading: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes full pipeline for an IoT sensor anomaly:
        1. Water Sentinel Agent (Thresholds & Weather filter)
        2. Source Investigator Agent (Upstream tracing)
        3. Dispatcher Agent (UPPCB / Rapid action team)
        """
        sentinel_res = water_sentinel_agent.process_sensor_node(node_id, reading)

        if sentinel_res.get("status") != "ANOMALY_CONFIRMED":
            return {
                "step": "WATER_SENTINEL",
                "status": sentinel_res.get("status"),
                "details": sentinel_res
            }

        ticket = sentinel_res["ticket"]
        ticket_id = ticket["id"]

        # Source Investigation
        invest_res = source_investigator_agent.investigate(ticket_id)

        # Dispatch
        dispatch_res = dispatcher_agent.dispatch(ticket_id)

        self.log("SENSOR_PIPELINE_EXECUTED", {
            "ticket_id": ticket_id,
            "flow": "SensorSpike -> WaterSentinel -> SourceInvestigator -> Dispatcher"
        })

        return {
            "status": "DISPATCHED",
            "ticket_id": ticket_id,
            "sentinel": sentinel_res,
            "investigation": invest_res,
            "dispatch": dispatch_res,
            "current_ticket": db.get_ticket(ticket_id)
        }

    def run_demo_step(self, scenario_id: str, step_index: int) -> Dict[str, Any]:
        """
        Interactive Step-by-Step Demo Runner for presentation:
        Scenario 'chemical_spike':
          Step 0: Initial state (Baseline)
          Step 1: Industrial Effluent Spike at Barrage (Sentinel triggers alert)
          Step 2: Source Investigator backtracks to Sahibabad Drain
          Step 3: Dispatcher assigns UPPCB Field Unit
          Step 4: Field cleanup & Verifier checks before/after + normalizes sensor
          Step 5: Briefing Agent issues IAS Executive Dossier
        """
        if scenario_id == "chemical_spike":
            if step_index == 1:
                # Trigger severe chemical spike on Node 2
                spike_data = {
                    "ph": 5.1,
                    "turbidity_ntu": 195.0,
                    "tds_ppm": 2480.0,
                    "temp_c": 29.0,
                    "lat": 28.6585,
                    "lng": 77.4185,
                    "node_name": "Hindon Barrage Central Sensor"
                }
                water_sentinel_agent.set_rainfall(0.0)  # Dry weather
                res = water_sentinel_agent.process_sensor_node("HIN-NODE-02", spike_data)
                return {
                    "step_name": "Sensor Spike Detected",
                    "agent": "Water Sentinel",
                    "description": "IoT Node HIN-NODE-02 at Hindon Barrage detected acidic pH (5.1) and severe TDS surge (2480 ppm). Rainfall filter confirmed dry weather; anomaly verified anthropogenic.",
                    "data": res
                }

            elif step_index == 2:
                # Source Investigator on the open ticket at barrage
                tickets = db.get_all_tickets()
                target_tkt = next((t for t in tickets if "HIN-NODE-02" in str(t.get("sensor_trigger"))), None)
                if not target_tkt:
                    target_tkt = tickets[0]
                res = source_investigator_agent.investigate(target_tkt["id"])
                return {
                    "step_name": "Upstream Source Investigation",
                    "agent": "Source Investigator",
                    "description": "Agent analyzed river flow vector and outfall catchment registry. Identified Sahibabad Industrial Drain (Site IV) as Top 1 culprit (89% confidence) with electroplating acid signature.",
                    "data": res
                }

            elif step_index == 3:
                # Dispatcher routes to UPPCB
                tickets = db.get_all_tickets()
                target_tkt = next((t for t in tickets if "HIN-NODE-02" in str(t.get("sensor_trigger"))), None)
                if not target_tkt:
                    target_tkt = tickets[0]
                res = dispatcher_agent.dispatch(target_tkt["id"])
                return {
                    "step_name": "Departmental Routing & Patrol Dispatch",
                    "agent": "Dispatcher",
                    "description": "Incident routed to UPPCB (Pollution Control Board). Rapid Response Unit PATROL-UPPCB-04 dispatched to inspect Sahibabad Drain outfall and seal illegal conduit.",
                    "data": res
                }

            elif step_index == 4:
                # Verifier checks remediation
                tickets = db.get_all_tickets()
                target_tkt = next((t for t in tickets if "HIN-NODE-02" in str(t.get("sensor_trigger"))), None)
                if not target_tkt:
                    target_tkt = tickets[0]
                res = verifier_agent.verify(
                    ticket_id=target_tkt["id"],
                    after_image_url="https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=800&q=80",
                    after_description="UPPCB team inspected Sahibabad Site IV outfall. Unauthorized electroplating conduit plugged with concrete. Foam dissipating; water clarity restored.",
                    force_pass=True
                )
                return {
                    "step_name": "Closed-Loop Verification",
                    "agent": "Verifier",
                    "description": "Before vs After vision model evaluated 92% cleanliness score. Downstream sensor confirmed pH restored to 7.3 and TDS normalized. Ticket marked VERIFIED_CLOSED.",
                    "data": res
                }

            elif step_index == 5:
                # Briefing Agent
                res = briefing_agent.generate_briefing()
                return {
                    "step_name": "Executive Command Briefing",
                    "agent": "Briefing Agent",
                    "description": "Daily intelligence report generated for District Magistrate in English and Hindi. Statutory show-cause notice drafted for errant industrial units.",
                    "data": res
                }

        elif scenario_id == "rain_runoff":
            # Rain runoff test
            water_sentinel_agent.set_rainfall(28.0)  # Heavy rain
            sim_reading = {
                "ph": 7.1,
                "turbidity_ntu": 180.0,
                "tds_ppm": 640.0,
                "temp_c": 24.5,
                "lat": 28.6940,
                "lng": 77.4080,
                "node_name": "Karhera Upstream Sensor"
            }
            res = water_sentinel_agent.process_sensor_node("HIN-NODE-01", sim_reading)
            return {
                "step_name": "Rainfall False-Alarm Filtering",
                "agent": "Water Sentinel",
                "description": f"Rainfall filter active (28mm precipitation). Turbidity rise (180 NTU) detected, but neutral pH and diluted TDS confirm natural silt runoff. No emergency dispatched.",
                "data": res
            }

        return {"error": f"Unknown scenario {scenario_id} or step {step_index}"}


# Singleton instance
orchestrator = SystemOrchestrator()
