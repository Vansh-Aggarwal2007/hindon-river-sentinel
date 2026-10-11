"""
Main FastAPI Application Entry Point for Hindon River Monitoring Command Center.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

from app.routes.tickets import router as tickets_router
from app.routes.sensors import router as sensors_router
from app.routes.agents import router as agents_router
from app.routes.briefing import router as briefing_router
from app.routes.demo import router as demo_router

app = FastAPI(
    title="Hindon River Rejuvenation — Multi-Agent Command Center",
    description="Intelligent monitoring, upstream source investigation, patrol dispatch, and verified closed-loop accountability system.",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(tickets_router)
app.include_router(sensors_router)
app.include_router(agents_router)
app.include_router(briefing_router)
app.include_router(demo_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "system": "Hindon River Monitoring Command Center",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents_active": [
            "Triage Agent",
            "Water Sentinel",
            "Source Investigator",
            "Dispatcher",
            "Verifier",
            "Briefing Agent",
            "System Orchestrator"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
