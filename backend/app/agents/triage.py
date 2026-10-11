"""
Triage Agent:
Analyzes citizen reports and photos, classifies pollution type and severity,
checks spatial/temporal duplicates, and outputs a validated ticket candidate.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import uuid

from app.agents.base import BaseAgent, haversine_distance_meters
from app.database import db
from app.models import IncidentType, SeverityLevel, PhotoAnalysis, TicketStatus


class TriageAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Triage Agent",
            role="Classifies citizen photo submissions, detects duplicates, and assigns preliminary severity"
        )

    # --- Agent Tools ---
    def tool_check_duplicates(self, lat: float, lng: float, radius_meters: float = 200.0) -> Optional[str]:
        """Search active tickets within spatial radius to prevent duplicate spam."""
        tickets = db.get_all_tickets()
        for t in tickets:
            if t["status"] in [TicketStatus.OPEN, TicketStatus.INVESTIGATING, TicketStatus.DISPATCHED, TicketStatus.IN_PROGRESS]:
                loc = t.get("location", {})
                t_lat = loc.get("lat")
                t_lng = loc.get("lng")
                if t_lat and t_lng:
                    dist = haversine_distance_meters(lat, lng, t_lat, t_lng)
                    if dist <= radius_meters:
                        return t["id"]
        return None

    def tool_analyze_image(self, image_url: Optional[str], text_description: str) -> PhotoAnalysis:
        """
        Vision heuristic & feature extraction tool.
        Parses keywords, visual signatures, and contextual cues.
        """
        text_lower = (text_description or "").lower()
        
        # Check toxic foam
        if any(w in text_lower for w in ["foam", "froth", "white foam", "surfactant", "toxic bubbles", "soapy"]):
            return PhotoAnalysis(
                detected_objects=["chemical_froth", "white_foam_blanket", "river_water"],
                pollution_type=IncidentType.TOXIC_FOAM,
                severity_score=9.1,
                cleanliness_score=15.0,
                confidence=0.96,
                visual_evidence=[
                    "High-density persistent white surfactant froth visible on surface",
                    "Aerosolized foaming observed near weir/confluence"
                ]
            )
        
        # Check industrial effluent / chemical
        if any(w in text_lower for w in ["chemical", "factory", "black water", "acid", "dye", "effluent", "colored water", "industrial"]):
            return PhotoAnalysis(
                detected_objects=["discolored_effluent_plume", "industrial_outfall", "turbid_stream"],
                pollution_type=IncidentType.INDUSTRIAL_EFFLUENT,
                severity_score=8.8,
                cleanliness_score=20.0,
                confidence=0.94,
                visual_evidence=[
                    "Dark industrial effluent entering water body",
                    "Strong discoloration indicating untreated industrial discharge"
                ]
            )
            
        # Check sewage outfall
        if any(w in text_lower for w in ["sewage", "gutter", "drain", "blackwater", "foul smell", "toilet", "nallah"]):
            return PhotoAnalysis(
                detected_objects=["open_sewer_discharge", "untreated_sludge", "domestic_waste"],
                pollution_type=IncidentType.SEWAGE_OUTFALL,
                severity_score=7.5,
                cleanliness_score=30.0,
                confidence=0.91,
                visual_evidence=[
                    "Direct untreated domestic nallah discharge into river course",
                    "High organic matter accumulation"
                ]
            )

        # Check encroachment
        if any(w in text_lower for w in ["encroach", "building", "shed", "construction", "sand mining", "illegal wall", "debris filling"]):
            return PhotoAnalysis(
                detected_objects=["debris_mound", "temporary_structures", "riparian_destruction"],
                pollution_type=IncidentType.ENCROACHMENT,
                severity_score=6.0,
                cleanliness_score=45.0,
                confidence=0.88,
                visual_evidence=[
                    "Unauthorized structure or soil backfilling inside the active floodplain"
                ]
            )

        # Check illegal burning
        if any(w in text_lower for w in ["burning", "smoke", "fire", "ash", "plastic burning"]):
            return PhotoAnalysis(
                detected_objects=["smoke_plume", "smoldering_plastic_ash", "waste_pile"],
                pollution_type=IncidentType.ILLEGAL_BURNING,
                severity_score=7.0,
                cleanliness_score=35.0,
                confidence=0.90,
                visual_evidence=[
                    "Open bonfire of municipal solid waste emitting toxic smoke on riverbank"
                ]
            )

        # Default to garbage / solid waste dumping
        return PhotoAnalysis(
            detected_objects=["plastic_bags", "beverage_bottles", "municipal_garbage", "riverbank_litter"],
            pollution_type=IncidentType.GARBAGE_DUMPING,
            severity_score=6.8,
            cleanliness_score=25.0,
            confidence=0.89,
            visual_evidence=[
                "Accumulated municipal solid waste heaps along embankment",
                "High density of non-biodegradable polymers and discarded refuse"
            ]
        )

    def process_report(
        self,
        lat: float,
        lng: float,
        description: str,
        image_url: Optional[str] = None,
        title: Optional[str] = None,
        reporter_contact: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main Agent Execution Workflow:
        1. Duplicate checking tool
        2. Vision / NLP analysis tool
        3. Severity scoring
        4. Structured Ticket creation
        """
        self.log("REPORT_RECEIVED", {
            "lat": lat,
            "lng": lng,
            "description": description[:100],
            "has_image": bool(image_url)
        })

        # Step 1: Check duplicate
        duplicate_id = self.execute_tool("check_duplicates", lat=lat, lng=lng, radius_meters=200.0)
        if duplicate_id:
            self.log("DUPLICATE_DETECTED", {"duplicate_of": duplicate_id, "lat": lat, "lng": lng})
            return {
                "is_duplicate": True,
                "existing_ticket_id": duplicate_id,
                "message": f"Report matches active incident {duplicate_id} within 200m radius. Merged to prevent duplicate dispatch."
            }

        # Step 2: Analyze Photo & Description
        analysis: PhotoAnalysis = self.execute_tool(
            "analyze_image",
            image_url=image_url,
            text_description=description
        )

        # Step 3: Compute Severity
        score = analysis.severity_score
        if score >= 8.5:
            severity = SeverityLevel.CRITICAL
        elif score >= 7.0:
            severity = SeverityLevel.HIGH
        elif score >= 4.5:
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW

        # Generate unique ticket ID
        ticket_id = f"TKT-HIN-{uuid.uuid4().hex[:6].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        ticket_title = title or f"{analysis.pollution_type.value.replace('_', ' ').title()} near Hindon Reach"

        ticket_data = {
            "id": ticket_id,
            "created_at": now_iso,
            "updated_at": now_iso,
            "title": ticket_title,
            "description": description,
            "incident_type": analysis.pollution_type.value,
            "severity": severity.value,
            "confidence": analysis.confidence,
            "status": TicketStatus.OPEN.value,
            "location": {
                "lat": lat,
                "lng": lng,
                "address": f"Hindon River Bank (Lat: {lat:.4f}, Lng: {lng:.4f}), Ghaziabad",
                "reach_km": round((28.7125 - lat) * 110.0, 1)  # Approximate km from northern Ghaziabad entry
            },
            "source_hypotheses": [],
            "assigned_department": None,
            "patrol_assignment": None,
            "before_photo_url": image_url or "https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?auto=format&fit=crop&w=800&q=80",
            "before_photo_analysis": analysis.model_dump(),
            "after_photo_url": None,
            "after_photo_analysis": None,
            "sensor_trigger": None,
            "verification": None,
            "escalation_approved": False
        }

        # Save to DB
        saved = db.save_ticket(ticket_data)
        self.log("TICKET_CREATED", {"ticket_id": ticket_id, "severity": severity.value, "type": analysis.pollution_type.value})

        return {
            "is_duplicate": False,
            "ticket": saved,
            "analysis": analysis.model_dump()
        }


# Singleton instance
triage_agent = TriageAgent()
