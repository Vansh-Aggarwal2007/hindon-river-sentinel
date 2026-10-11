"""
Database module for Hindon River Monitoring System.
Provides thread-safe in-memory + SQLite storage with seed initialization.
"""
import copy
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from app.models import Ticket, SensorReading, AgentLog
from app.seed_data import (
    HINDON_RIVER_COORDINATES,
    DRAINS_DATA,
    SENSOR_NODES_DATA,
    INITIAL_TICKETS
)

_LOCK = threading.Lock()

class Database:
    def __init__(self, db_path: str = "hindon_river.db"):
        self.db_path = db_path
        self._tickets: Dict[str, Dict[str, Any]] = {}
        self._sensors: Dict[str, Dict[str, Any]] = {}
        self._drains: List[Dict[str, Any]] = copy.deepcopy(DRAINS_DATA)
        self._river_coords: List[List[float]] = copy.deepcopy(HINDON_RIVER_COORDINATES)
        self._logs: List[Dict[str, Any]] = []
        self._init_sqlite()
        self.reset()

    def _init_sqlite(self):
        """Initialize SQLite tables for persistent backup."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT NOT NULL
                )
            """)
            conn.commit()

    def reset(self):
        """Reset state to default seed data for reproducible demo replays."""
        with _LOCK:
            self._tickets = {t["id"]: copy.deepcopy(t) for t in INITIAL_TICKETS}
            self._sensors = {s["node_id"]: copy.deepcopy(s) for s in SENSOR_NODES_DATA}
            self._drains = copy.deepcopy(DRAINS_DATA)
            self._river_coords = copy.deepcopy(HINDON_RIVER_COORDINATES)
            self._logs = [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "agent_name": "System Orchestrator",
                    "action": "SYSTEM_INITIALIZED",
                    "details": {"message": "Hindon River Monitoring Command Center started."}
                }
            ]

    # --- Tickets ---
    def get_all_tickets(self) -> List[Dict[str, Any]]:
        with _LOCK:
            return list(self._tickets.values())

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        with _LOCK:
            return copy.deepcopy(self._tickets.get(ticket_id))

    def save_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        with _LOCK:
            tid = ticket_data["id"]
            ticket_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._tickets[tid] = copy.deepcopy(ticket_data)
            
            # Persist to SQLite
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT OR REPLACE INTO tickets (id, data, created_at) VALUES (?, ?, ?)",
                        (tid, json.dumps(ticket_data), ticket_data.get("created_at", ""))
                    )
                    conn.commit()
            except Exception:
                pass
            return copy.deepcopy(ticket_data)

    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with _LOCK:
            if ticket_id not in self._tickets:
                return None
            self._tickets[ticket_id].update(updates)
            self._tickets[ticket_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
            data = copy.deepcopy(self._tickets[ticket_id])
            
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE tickets SET data = ? WHERE id = ?",
                        (json.dumps(data), ticket_id)
                    )
                    conn.commit()
            except Exception:
                pass
            return data

    def delete_ticket(self, ticket_id: str) -> bool:
        with _LOCK:
            if ticket_id in self._tickets:
                del self._tickets[ticket_id]
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
                        conn.commit()
                except Exception:
                    pass
                return True
            return False

    # --- Sensors ---
    def get_all_sensors(self) -> List[Dict[str, Any]]:
        with _LOCK:
            return list(self._sensors.values())

    def get_sensor(self, node_id: str) -> Optional[Dict[str, Any]]:
        with _LOCK:
            return copy.deepcopy(self._sensors.get(node_id))

    def update_sensor_reading(self, node_id: str, reading: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with _LOCK:
            if node_id in self._sensors:
                self._sensors[node_id]["current"].update(reading)
                return copy.deepcopy(self._sensors[node_id])
            return None

    # --- Drains & River ---
    def get_all_drains(self) -> List[Dict[str, Any]]:
        with _LOCK:
            return copy.deepcopy(self._drains)

    def get_drain(self, drain_id: str) -> Optional[Dict[str, Any]]:
        with _LOCK:
            for d in self._drains:
                if d["id"] == drain_id:
                    return copy.deepcopy(d)
            return None

    def get_river_coordinates(self) -> List[List[float]]:
        with _LOCK:
            return copy.deepcopy(self._river_coords)

    # --- Logs ---
    def add_log(self, agent_name: str, action: str, details: Dict[str, Any]) -> Dict[str, Any]:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_name": agent_name,
            "action": action,
            "details": details
        }
        with _LOCK:
            self._logs.insert(0, log_entry)  # Latest first
            if len(self._logs) > 200:
                self._logs.pop()
        return log_entry

    def get_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with _LOCK:
            return copy.deepcopy(self._logs[:limit])


# Global database singleton
db = Database()
