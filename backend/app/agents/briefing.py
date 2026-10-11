"""
Briefing Agent:
Synthesizes telemetry and ticketing metrics into an Executive Daily Briefing
for the District Magistrate / IAS Officer heading the Hindon River Rejuvenation Mission.
Generates bilingual reports (English + Hindi), flags overdue tickets, and drafts statutory notices.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.agents.base import BaseAgent
from app.database import db
from app.models import TicketStatus, SeverityLevel


class BriefingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Briefing Agent",
            role="Generates bilingual daily executive intelligence dossiers and statutory escalation notices"
        )

    # --- Agent Tools ---
    def tool_aggregate_statistics(self) -> Dict[str, Any]:
        """Calculates command center operational metrics."""
        tickets = db.get_all_tickets()
        sensors = db.get_all_sensors()

        total = len(tickets)
        open_count = sum(1 for t in tickets if t["status"] in [TicketStatus.OPEN.value, TicketStatus.INVESTIGATING.value])
        dispatched_count = sum(1 for t in tickets if t["status"] in [TicketStatus.DISPATCHED.value, TicketStatus.IN_PROGRESS.value])
        pending_verif = sum(1 for t in tickets if t["status"] == TicketStatus.PENDING_VERIFICATION.value)
        closed_count = sum(1 for t in tickets if t["status"] == TicketStatus.VERIFIED_CLOSED.value)
        reopened_count = sum(1 for t in tickets if t["status"] == TicketStatus.REOPENED.value)

        critical_tickets = [t for t in tickets if t.get("severity") == SeverityLevel.CRITICAL.value and t["status"] != TicketStatus.VERIFIED_CLOSED.value]
        active_sensor_anomalies = [s for s in sensors if s.get("current", {}).get("is_anomaly", False)]

        # Compliance rate
        resolution_rate = round((closed_count / total * 100.0) if total > 0 else 0.0, 1)

        return {
            "total_tickets": total,
            "open_count": open_count,
            "dispatched_count": dispatched_count,
            "pending_verification": pending_verif,
            "closed_count": closed_count,
            "reopened_count": reopened_count,
            "resolution_rate_percent": resolution_rate,
            "critical_tickets": critical_tickets,
            "active_sensor_anomalies": active_sensor_anomalies
        }

    def tool_generate_english_dossier(self, stats: Dict[str, Any]) -> str:
        """Constructs high-level English briefing for IAS administration."""
        date_str = datetime.now(timezone.utc).strftime("%d %B %Y")
        crit_list = ""
        for ct in stats["critical_tickets"]:
            crit_list += f"- **[{ct['id']}] {ct['title']}**: Reach {ct['location']['reach_km']} km | Dept: {ct.get('assigned_department', 'Unassigned')} | Status: {ct['status']}\n"

        if not crit_list:
            crit_list = "- *No critical unaddressed breaches currently flagged.*\n"

        dossier = f"""# Hindon River Rejuvenation Drive — Daily Command Briefing
**Date:** {date_str} | **Monitoring Sector:** Ghaziabad District Corridor (Karhera to NH-24)
**Command Authority:** District Magistrate & Special Task Force on Hindon River

---

### 1. Executive Operations Summary
- **Total Incidents Logged:** {stats['total_tickets']}
- **Verified Resolutions (Closed):** {stats['closed_count']} ({stats['resolution_rate_percent']}%)
- **Active Patrol Dispatches:** {stats['dispatched_count']}
- **Awaiting Verification Review:** {stats['pending_verification']}
- **Reopened (Audit Failure):** {stats['reopened_count']}
- **Active Water Sensor Anomalies:** {len(stats['active_sensor_anomalies'])}

---

### 2. High-Priority Red Flag Zones
{crit_list}

---

### 3. Source Investigation & Enforcement Alerts
- **Sahibabad Site IV Industrial Belt:** Chemical fingerprint correlation confirms persistent acidic discharges into Sahibabad Drain. Immediate inspection recommended.
- **Municipal Waste Hotspots:** Karhera Ghat embankment cleared; automated surveillance recommended to prevent repeat dumping.
"""
        return dossier

    def tool_generate_hindi_summary(self, stats: Dict[str, Any]) -> str:
        """Constructs official Hindi (हिंदी) briefing for field officers and local administration."""
        date_str = datetime.now(timezone.utc).strftime("%d %B %Y")
        
        hindi_text = f"""### हिंडन नदी स्वच्छता निगरानी अभियान — दैनिक प्रशासनिक सारांश
**दिनांक:** {date_str} | **प्रक्षेत्र:** गाजियाबाद (करहेड़ा से एनएच-24 हिंडन बैराज)

- **कुल दर्ज मामले:** {stats['total_tickets']}
- **सत्यापित एवं निस्तारित (Verified Closed):** {stats['closed_count']}
- **मौके पर सक्रिय टीमें (Patrol Dispatched):** {stats['dispatched_count']}
- **पुनः खुले मामले (सफाई अधूरी पाई गई):** {stats['reopened_count']}
- **सक्रिय सेंसर अलार्म:** {len(stats['active_sensor_anomalies'])}

**विशेष निर्देश:** 
साहिबाबाद नाले और हिंडन बैराज पर रसायनों और झाग की निगरानी हेतु UPPCB की संयुक्त टीम को चालान एवं निरीक्षण के निर्देश दिए जाएं। करहेड़ा घाट पर दोबारा कचरा फेंकने वालों पर नगर निगम द्वारा सख्त दंडात्मक कार्रवाई सुनिश्चित की जाए।"""
        return hindi_text

    def tool_draft_statutory_notice(self, ticket: Dict[str, Any]) -> str:
        """Drafts formal statutory legal notice under Section 33A of Water Act 1974."""
        tid = ticket["id"]
        title = ticket["title"]
        loc = ticket["location"]
        dept = ticket.get("assigned_department", "Uttar Pradesh Pollution Control Board")
        date_str = datetime.now(timezone.utc).strftime("%d/%m/%Y")

        notice = f"""OFFICE OF THE DISTRICT MAGISTRATE & CHAIRMAN, HINDON REVIVAL TASK FORCE
COLLECTORATE COMPOUND, GHAZIABAD, UTTAR PRADESH

MEMORANDUM / SHOW CAUSE DIRECTIVE UNDER SECTION 33A, WATER ACT 1974
Reference Incident ID: {tid}
Date of Notice: {date_str}

TO:
The Regional Officer, {dept} / Occupier of Associated Effluent Conduit
Location: {loc.get('address')} (GPS: {loc.get('lat')}, {loc.get('lng')})

SUBJECT: IMMEDIATE SHOW-CAUSE AND CLOSURE DIRECTIVE REGARDING UNTREATED DISCHARGE INTO HINDON RIVER

1. Automated telemetry and multi-agent surveillance have documented severe contamination: "{title}".
2. Multi-point sensor analysis confirms chemical parameters in violation of Section 24 of the Water (Prevention and Control of Pollution) Act 1974.
3. You are hereby directed to submit an Action Taken Report (ATR) along with verifiable photographic and sensor rectification records within 48 hours.
4. Failure to comply shall invite immediate sealing of discharge conduits and prosecution under Section 43/44 of the Act.

By Order of the Competent Authority,
District Magistrate, Ghaziabad
"""
        return notice

    def generate_briefing(self) -> Dict[str, Any]:
        """
        Main Agent Execution Workflow:
        1. Aggregate metrics across all agents & tickets
        2. Draft English executive briefing
        3. Draft Hindi briefing
        4. Return complete briefing dossier
        """
        stats = self.execute_tool("aggregate_statistics")
        english_dossier = self.execute_tool("generate_english_dossier", stats=stats)
        hindi_summary = self.execute_tool("generate_hindi_summary", stats=stats)

        self.log("BRIEFING_GENERATED", {
            "total_tickets": stats["total_tickets"],
            "resolution_rate": stats["resolution_rate_percent"],
            "critical_count": len(stats["critical_tickets"])
        })

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "stats": stats,
            "english_dossier": english_dossier,
            "hindi_summary": hindi_summary
        }

    def escalate_and_draft_notice(self, ticket_id: str, officer_notes: str) -> Dict[str, Any]:
        """Approves formal statutory escalation for a ticket."""
        ticket = db.get_ticket(ticket_id)
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}

        notice = self.execute_tool("draft_statutory_notice", ticket=ticket)
        
        # Update ticket
        updates = {
            "escalation_approved": True,
            "escalation_notes": officer_notes
        }
        updated_ticket = db.update_ticket(ticket_id, updates)

        self.log("ESCALATION_APPROVED", {
            "ticket_id": ticket_id,
            "officer_notes": officer_notes
        })

        return {
            "ticket_id": ticket_id,
            "escalation_approved": True,
            "statutory_notice": notice,
            "ticket": updated_ticket
        }


# Singleton instance
briefing_agent = BriefingAgent()
