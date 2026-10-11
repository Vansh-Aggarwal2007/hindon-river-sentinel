"""
FastAPI routes for District Magistrate / IAS Daily Briefing and statutory escalations.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.agents.briefing import briefing_agent

router = APIRouter(prefix="/api/briefing", tags=["Briefing & Governance"])


class EscalateInput(BaseModel):
    officer_notes: str = "Approved for statutory show-cause directive under Section 33A Water Act 1974."


@router.get("")
def get_daily_briefing() -> Dict[str, Any]:
    return briefing_agent.generate_briefing()


@router.post("/escalate/{ticket_id}")
def escalate_ticket(ticket_id: str, data: EscalateInput) -> Dict[str, Any]:
    res = briefing_agent.escalate_and_draft_notice(ticket_id, data.officer_notes)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
