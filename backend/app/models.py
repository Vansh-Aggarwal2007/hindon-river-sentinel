"""
Domain models and schemas for Hindon River Monitoring System.
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class IncidentType(str, Enum):
    GARBAGE_DUMPING = "garbage_dumping"
    TOXIC_FOAM = "toxic_foam"
    SEWAGE_OUTFALL = "sewage_outfall"
    INDUSTRIAL_EFFLUENT = "industrial_effluent"
    ENCROACHMENT = "encroachment"
    ILLEGAL_BURNING = "illegal_burning"
    WATER_ANOMALY = "water_anomaly"


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    DISPATCHED = "DISPATCHED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED_CLOSED = "VERIFIED_CLOSED"
    REOPENED = "REOPENED"


class Department(str, Enum):
    UPPCB = "UPPCB (Pollution Control Board)"
    NAGAR_NIGAM = "Nagar Nigam Ghaziabad"
    JAL_NIGAM = "UP Jal Nigam"
    IRRIGATION = "UP Irrigation Department"


class Location(BaseModel):
    lat: float
    lng: float
    address: str = "Hindon River Stretch, Ghaziabad"
    reach_km: float = 0.0


class SourceHypothesis(BaseModel):
    source_id: str
    name: str
    drain_id: str
    type: str  # e.g., 'industrial_cluster', 'sewer_trunk', 'slaughterhouse_drain'
    confidence: float
    distance_upstream_m: float
    evidence: List[str] = []


class PatrolAssignment(BaseModel):
    officer_name: str
    patrol_id: str
    dispatched_at: str
    target_eta: str
    route_order: int = 1


class PhotoAnalysis(BaseModel):
    detected_objects: List[str] = []
    pollution_type: IncidentType
    severity_score: float = 0.0  # 0 to 10
    cleanliness_score: float = 0.0  # 0 to 100
    confidence: float = 0.0
    visual_evidence: List[str] = []


class SensorReading(BaseModel):
    node_id: str
    node_name: str
    timestamp: str
    lat: float
    lng: float
    ph: float
    turbidity_ntu: float
    tds_ppm: float
    temp_c: float
    is_anomaly: bool = False
    anomaly_reason: Optional[str] = None


class VerificationResult(BaseModel):
    verified: bool
    status: TicketStatus
    before_cleanliness: float
    after_cleanliness: float
    improvement_percentage: float
    sensor_normalized: bool
    rejection_reasons: List[str] = []
    notes: str


class Ticket(BaseModel):
    id: str
    created_at: str
    updated_at: str
    title: str
    description: str
    incident_type: IncidentType
    severity: SeverityLevel
    confidence: float
    status: TicketStatus
    location: Location
    source_hypotheses: List[SourceHypothesis] = []
    assigned_department: Optional[Department] = None
    patrol_assignment: Optional[PatrolAssignment] = None
    before_photo_url: Optional[str] = None
    before_photo_analysis: Optional[PhotoAnalysis] = None
    after_photo_url: Optional[str] = None
    after_photo_analysis: Optional[PhotoAnalysis] = None
    sensor_trigger: Optional[Dict[str, Any]] = None
    verification: Optional[VerificationResult] = None
    escalation_approved: bool = False
    escalation_notes: Optional[str] = None


class ReportSubmission(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    lat: float
    lng: float
    reporter_contact: Optional[str] = None


class AgentLog(BaseModel):
    timestamp: str
    agent_name: str
    action: str
    details: Dict[str, Any] = {}
