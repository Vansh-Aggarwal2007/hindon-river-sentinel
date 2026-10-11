"""
Base Agent class and common utilities for multi-agent reasoning.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import math
from app.database import db


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def log(self, action: str, details: Dict[str, Any]):
        """Record agent action to database log."""
        return db.add_log(self.name, action, details)

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Helper to invoke tools and track execution."""
        tool_method = getattr(self, f"tool_{tool_name}", None)
        if not tool_method:
            raise ValueError(f"Tool {tool_name} not found on agent {self.name}")
        result = tool_method(**kwargs)
        self.log(f"TOOL_CALL:{tool_name}", {"parameters": kwargs, "result_summary": str(result)[:200]})
        return result
