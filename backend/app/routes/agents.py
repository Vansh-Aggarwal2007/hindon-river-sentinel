"""
FastAPI routes for executing individual agents and querying agent logs.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.database import db
from app.agents.triage import triage_agent
from app.agents.source_investigator import source_investigator_agent
from app.agents.dispatcher import dispatcher_agent
from app.agents.verifier import verifier_agent

router = APIRouter(prefix="/api/agents", tags=["Agents"])


class VerifyInput(BaseModel):
    after_image_url: Optional[str] = None
    after_description: Optional[str] = None
    force_pass: Optional[bool] = None


@router.post("/investigate/{ticket_id}")
def trigger_source_investigator(ticket_id: str) -> Dict[str, Any]:
    res = source_investigator_agent.investigate(ticket_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@router.post("/dispatch/{ticket_id}")
def trigger_dispatcher(ticket_id: str) -> Dict[str, Any]:
    res = dispatcher_agent.dispatch(ticket_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@router.post("/verify/{ticket_id}")
def trigger_verifier(ticket_id: str, data: VerifyInput) -> Dict[str, Any]:
    res = verifier_agent.verify(
        ticket_id=ticket_id,
        after_image_url=data.after_image_url,
        after_description=data.after_description,
        force_pass=data.force_pass
    )
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@router.get("/logs")
def get_agent_logs(limit: int = 50) -> List[Dict[str, Any]]:
    return db.get_logs(limit=limit)


@router.post("/reset")
def reset_database() -> Dict[str, Any]:
    db.reset()
    return {"success": True, "message": "Database and tickets reset to initial seed scenario."}
