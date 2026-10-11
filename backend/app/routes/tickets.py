"""
FastAPI routes for incident tickets.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.database import db
from app.agents.triage import triage_agent
from app.models import ReportSubmission

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.get("")
def list_tickets() -> List[Dict[str, Any]]:
    return db.get_all_tickets()


@router.get("/{ticket_id}")
def get_ticket(ticket_id: str) -> Dict[str, Any]:
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("")
def create_report(submission: ReportSubmission) -> Dict[str, Any]:
    """Submit report via citizen or patrol app; triggers Triage Agent."""
    res = triage_agent.process_report(
        lat=submission.lat,
        lng=submission.lng,
        description=submission.description or "Unspecified environmental concern reported near riverbank.",
        image_url=submission.image_url,
        title=submission.title,
        reporter_contact=submission.reporter_contact
    )
    return res


@router.put("/{ticket_id}")
def update_ticket(ticket_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    updated = db.update_ticket(ticket_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return updated


@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: str) -> Dict[str, Any]:
    deleted = db.delete_ticket(ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"success": True, "ticket_id": ticket_id}
