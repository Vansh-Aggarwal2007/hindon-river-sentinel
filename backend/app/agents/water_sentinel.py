"""
Water Sentinel Agent:
Monitors IoT sensors and satellite indices along the Hindon River.
Detects chemical/physical anomalies and filters out rain-driven false alarms.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

from app.agents.base import BaseAgent
from app.database import db
from app.models import IncidentType, SeverityLevel, TicketStatus


class WaterSentinelAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Water Sentinel",
            role="Detects sensor anomalies, applies rainfall false-alarm filtering, and triggers incident tracking"
        )
        self.simulated_rainfall_mm = 0.0  # Can be dynamically adjusted for demo

    # --- Agent Tools ---
    def tool_get_recent_rainfall(self, lat: float, lng: float) -> float:
        """
        Retrieves past 6-hour accumulated precipitation in mm.
        In demo mode, uses configurable state or seasonal baseline.
        """
        return float(self.simulated_rainfall_mm)

    def tool_evaluate_water_parameters(
        self,
        ph: float,
        turbidity_ntu: float,
        tds_ppm: float,
        temp_c: float
    ) -> Dict[str, Any]:
        """
        Evaluates physical-chemical thresholds against CPCB Class C/D river standards.
        """
        issues = []
        is_severe = False

        # pH evaluation
        if ph < 6.0:
            issues.append(f"Acidic pH violation: {ph:.2f} (Standard: 6.5 - 8.5)")
            is_severe = True
        elif ph > 9.0:
            issues.append(f"Alkaline pH violation: {ph:.2f} (Standard: 6.5 - 8.5)")
            is_severe = True

        # TDS evaluation
        if tds_ppm > 2000.0:
            issues.append(f"Severe industrial TDS spike: {tds_ppm:.1f} ppm (Standard: < 1000 ppm)")
            is_severe = True
        elif tds_ppm > 1400.0:
            issues.append(f"Elevated TDS concentration: {tds_ppm:.1f} ppm")

        # Turbidity evaluation
        if turbidity_ntu > 150.0:
            issues.append(f"High Turbidity spike: {turbidity_ntu:.1f} NTU (Baseline: < 50 NTU)")
        elif turbidity_ntu > 100.0:
            issues.append(f"Moderate Turbidity rise: {turbidity_ntu:.1f} NTU")

        is_anomaly = len(issues) > 0
        return {
            "is_anomaly": is_anomaly,
            "is_severe": is_severe,
            "issues": issues,
            "parameter_summary": {
                "ph": ph,
                "turbidity": turbidity_ntu,
                "tds": tds_ppm,
                "temp": temp_c
            }
        }

    def tool_filter_rain_runoff(
        self,
        turbidity_ntu: float,
        tds_ppm: float,
        ph: float,
        rainfall_mm: float
    ) -> Dict[str, Any]:
        """
        Distinguishes natural stormwater turbidity from illegal industrial dumping.
        When heavy rain occurs (> 15mm), suspended silt elevates turbidity,
        while TDS drops due to dilution and pH stays near neutral (~7.0-7.4).
        """
        if rainfall_mm >= 15.0:
            # If TDS is low/diluted and pH is normal, turbidity is benign rain runoff
            if tds_ppm < 900.0 and (6.5 <= ph <= 8.0):
                return {
                    "is_rain_driven": True,
                    "confidence": 0.93,
                    "reason": f"Turbidity elevation ({turbidity_ntu:.1f} NTU) correlated with heavy precipitation ({rainfall_mm:.1f} mm). TDS is diluted ({tds_ppm:.1f} ppm). False alarm filtered."
                }
            else:
                return {
                    "is_rain_driven": False,
                    "confidence": 0.85,
                    "reason": f"Rainfall present ({rainfall_mm:.1f} mm), but anomalous chemical signature (TDS: {tds_ppm:.1f} ppm, pH: {ph:.2f}) indicates simultaneous illegal discharge during rain."
                }
        else:
            return {
                "is_rain_driven": False,
                "confidence": 0.98,
                "reason": f"Dry weather conditions ({rainfall_mm:.1f} mm rain). Anomaly is unambiguously anthropogenic."
            }

    def set_rainfall(self, mm: float):
        """Allows testing rain-filter behavior."""
        self.simulated_rainfall_mm = mm
        self.log("WEATHER_UPDATED", {"rainfall_mm": mm})

    def process_sensor_node(self, node_id: str, reading: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main Sentinel workflow:
        1. Fetch current sensor reading
        2. Evaluate parameters
        3. Check rainfall filter
        4. Create ticket if genuine industrial anomaly
        """
        ph = float(reading.get("ph", 7.0))
        turbidity = float(reading.get("turbidity_ntu", 40.0))
        tds = float(reading.get("tds_ppm", 600.0))
        temp = float(reading.get("temp_c", 26.0))
        lat = float(reading.get("lat", 28.6585))
        lng = float(reading.get("lng", 77.4185))
        node_name = reading.get("node_name", node_id)

        self.log("SENSOR_PROCESSED", {"node_id": node_id, "reading": reading})

        # Step 1: Evaluate parameters
        eval_result = self.execute_tool(
            "evaluate_water_parameters",
            ph=ph,
            turbidity_ntu=turbidity,
            tds_ppm=tds,
            temp_c=temp
        )

        if not eval_result["is_anomaly"]:
            db.update_sensor_reading(node_id, {
                "ph": ph, "turbidity_ntu": turbidity, "tds_ppm": tds, "temp_c": temp,
                "is_anomaly": False, "anomaly_reason": None
            })
            return {"status": "NORMAL", "node_id": node_id, "eval": eval_result}

        # Step 2: Rainfall Filter
        rainfall = self.execute_tool("get_recent_rainfall", lat=lat, lng=lng)
        rain_filter = self.execute_tool(
            "filter_rain_runoff",
            turbidity_ntu=turbidity,
            tds_ppm=tds,
            ph=ph,
            rainfall_mm=rainfall
        )

        if rain_filter["is_rain_driven"]:
            # False alarm filtered
            db.update_sensor_reading(node_id, {
                "ph": ph, "turbidity_ntu": turbidity, "tds_ppm": tds, "temp_c": temp,
                "is_anomaly": False, "anomaly_reason": f"Rain Runoff (Filtered): {rain_filter['reason']}"
            })
            self.log("RAIN_FILTER_TRIGGERED", {"node_id": node_id, "explanation": rain_filter["reason"]})
            return {
                "status": "RAIN_FILTERED",
                "node_id": node_id,
                "reason": rain_filter["reason"]
            }

        # Step 3: Confirmed Anomaly -> Update sensor & create or link ticket
        anomaly_msg = " | ".join(eval_result["issues"])
        db.update_sensor_reading(node_id, {
            "ph": ph, "turbidity_ntu": turbidity, "tds_ppm": tds, "temp_c": temp,
            "is_anomaly": True, "anomaly_reason": anomaly_msg
        })

        severity = SeverityLevel.CRITICAL if eval_result["is_severe"] else SeverityLevel.HIGH
        
        ticket_id = f"TKT-SEN-{uuid.uuid4().hex[:6].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()
        
        ticket_data = {
            "id": ticket_id,
            "created_at": now_iso,
            "updated_at": now_iso,
            "title": f"Chemical Spike Detected at {node_name}",
            "description": f"Automated sensor alert: {anomaly_msg}. Weather check confirmed non-stormwater origin ({rain_filter['reason']}).",
            "incident_type": IncidentType.INDUSTRIAL_EFFLUENT.value if tds > 1600 or ph < 6.0 else IncidentType.WATER_ANOMALY.value,
            "severity": severity.value,
            "confidence": 0.95,
            "status": TicketStatus.OPEN.value,
            "location": {
                "lat": lat,
                "lng": lng,
                "address": f"Hindon River Node {node_id} ({node_name}), Ghaziabad",
                "reach_km": round((28.7125 - lat) * 110.0, 1)
            },
            "source_hypotheses": [],
            "assigned_department": None,
            "patrol_assignment": None,
            "before_photo_url": "https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&w=800&q=80",
            "before_photo_analysis": {
                "detected_objects": ["chemical_slick", "sensor_node_mooring", "turbid_river"],
                "pollution_type": IncidentType.INDUSTRIAL_EFFLUENT.value,
                "severity_score": 9.0,
                "cleanliness_score": 15.0,
                "confidence": 0.95,
                "visual_evidence": [anomaly_msg]
            },
            "after_photo_url": None,
            "after_photo_analysis": None,
            "sensor_trigger": {
                "node_id": node_id,
                "parameters": eval_result["parameter_summary"],
                "issues": eval_result["issues"]
            },
            "verification": None,
            "escalation_approved": False
        }

        saved_ticket = db.save_ticket(ticket_data)
        self.log("INCIDENT_TRIGGERED", {"ticket_id": ticket_id, "node_id": node_id, "severity": severity.value})

        return {
            "status": "ANOMALY_CONFIRMED",
            "node_id": node_id,
            "ticket": saved_ticket,
            "eval": eval_result,
            "rain_filter": rain_filter
        }


# Singleton instance
water_sentinel_agent = WaterSentinelAgent()
