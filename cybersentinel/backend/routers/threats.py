"""
TICKET-029 — Threats router.
GET /threats: returns history of all detected threats in the current session.
threat_store is an in-memory list — resets on server restart.
"""
from fastapi import APIRouter

router = APIRouter()

# In-memory session store — all detected threats for the current run
threat_store: list[dict] = []


@router.get("/threats")
def get_threats():
    return threat_store
