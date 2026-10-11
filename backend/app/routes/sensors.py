"""
FastAPI routes for IoT Sensor telemetry, river coordinates, and drains.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from app.database import db
from app.agents.water_sentinel import water_sentinel_agent

router = APIRouter(prefix="/api", tags=["Sensors & River GIS"])


class ReadingInput(BaseModel):
    ph: float
    turbidity_ntu: float
    tds_ppm: float
    temp_c: float = 26.0


class RainfallInput(BaseModel):
    rainfall_mm: float


@router.get("/sensors")
def list_sensors() -> List[Dict[str, Any]]:
    return db.get_all_sensors()


@router.get("/sensors/{node_id}")
def get_sensor(node_id: str) -> Dict[str, Any]:
    sensor = db.get_sensor(node_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor node not found")
    return sensor


@router.post("/sensors/{node_id}/reading")
def post_sensor_reading(node_id: str, reading: ReadingInput) -> Dict[str, Any]:
    """Ingests sensor reading and triggers Water Sentinel evaluation."""
    sensor = db.get_sensor(node_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor node not found")

    reading_dict = {
        "ph": reading.ph,
        "turbidity_ntu": reading.turbidity_ntu,
        "tds_ppm": reading.tds_ppm,
        "temp_c": reading.temp_c,
        "lat": sensor.get("lat"),
        "lng": sensor.get("lng"),
        "node_name": sensor.get("node_name", node_id)
    }

    res = water_sentinel_agent.process_sensor_node(node_id, reading_dict)
    return res


@router.post("/sensors/set-rain")
def set_rain(input_data: RainfallInput) -> Dict[str, Any]:
    water_sentinel_agent.set_rainfall(input_data.rainfall_mm)
    return {"success": True, "rainfall_mm": input_data.rainfall_mm}


@router.get("/drains")
def list_drains() -> List[Dict[str, Any]]:
    return db.get_all_drains()


@router.get("/river-coords")
def get_river_coords() -> List[List[float]]:
    return db.get_river_coordinates()
