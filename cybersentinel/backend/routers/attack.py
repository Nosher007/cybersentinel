"""
TICKET-013 — Attack router.
POST /attack: starts a simulation scenario
POST /stop:   stops the running scenario
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from simulation.engine import SimulationEngine, SCENARIO_REGISTRY

router = APIRouter()

# Single shared engine instance — lives for the duration of the server process
engine = SimulationEngine()


class AttackRequest(BaseModel):
    scenario_id: str
    speed_multiplier: float = 100.0


@router.post("/attack")
async def start_attack(req: AttackRequest):
    if not req.scenario_id:
        raise HTTPException(status_code=400, detail="scenario_id cannot be empty")
    if req.scenario_id not in SCENARIO_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown scenario '{req.scenario_id}'. "
                   f"Available: {sorted(SCENARIO_REGISTRY.keys())}"
        )
    if engine.is_running:
        raise HTTPException(
            status_code=409,
            detail=f"Scenario '{engine.current_scenario_id}' is already running. POST /stop first."
        )

    await engine.start(req.scenario_id, speed_multiplier=req.speed_multiplier)
    return {"status": "started", "scenario_id": req.scenario_id}


@router.post("/stop")
async def stop_attack():
    await engine.stop()
    return {"status": "stopped"}
