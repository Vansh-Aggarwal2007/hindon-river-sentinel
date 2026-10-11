"""
FastAPI routes for hackathon presentation live replay scenarios.
"""
from fastapi import APIRouter
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.agents.orchestrator import orchestrator
from app.models import ReportSubmission

router = APIRouter(prefix="/api/demo", tags=["Demo Replay Engine"])


class StepInput(BaseModel):
    scenario_id: str = "chemical_spike"  # 'chemical_spike' or 'rain_runoff'
    step_index: int = 1


@router.post("/step")
def execute_demo_step(step_data: StepInput) -> Dict[str, Any]:
    """Runs a single atomic step in the replay scenario."""
    return orchestrator.run_demo_step(step_data.scenario_id, step_data.step_index)


@router.post("/citizen-report")
def run_live_citizen_report(report: ReportSubmission) -> Dict[str, Any]:
    """Runs live end-to-end multi-agent pipeline for a new citizen submission."""
    return orchestrator.run_end_to_end_citizen_report(
        lat=report.lat,
        lng=report.lng,
        description=report.description or "Plastic dumping reported near riverbank",
        image_url=report.image_url
    )
