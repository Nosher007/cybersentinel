"""
TICKET-027 — Attack router (updated).
POST /attack: interprets natural language prompt → starts simulation → triggers agent pipeline
POST /stop:   stops the running scenario
"""
import asyncio
import os
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from simulation.engine import SimulationEngine, SCENARIO_REGISTRY

try:
    from backend.agents.prompt_interpreter import AttackPromptInterpreter
except ModuleNotFoundError:
    from agents.prompt_interpreter import AttackPromptInterpreter

router = APIRouter()
_is_test = os.getenv("ENVIRONMENT", "").lower() == "test"
limiter = Limiter(key_func=get_remote_address, enabled=not _is_test)

engine = SimulationEngine()

MAX_PROMPT_LENGTH = 300


class AttackRequest(BaseModel):
    prompt: str


@router.post("/attack")
@limiter.limit("5/minute")
async def start_attack(request: Request, req: AttackRequest):
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt cannot be empty")

    if len(req.prompt) > MAX_PROMPT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Prompt too long. Maximum {MAX_PROMPT_LENGTH} characters."
        )

    if engine.is_running:
        raise HTTPException(
            status_code=409,
            detail=f"Scenario '{engine.current_scenario_id}' is already running. POST /stop first."
        )

    interpreter = AttackPromptInterpreter()
    try:
        interpreted = await asyncio.get_event_loop().run_in_executor(
            None, interpreter.interpret, req.prompt
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Attack interpretation failed. Please try again.")

    scenario_id = interpreted.scenario_id
    await engine.start(scenario_id)

    return {
        "status": "started",
        "scenario_id": scenario_id,
        "attack_type": interpreted.attack_type.value,
        "target_service": interpreted.target_service,
        "intensity": interpreted.intensity,
        "reasoning": interpreted.reasoning,
    }


@router.post("/stop")
async def stop_attack():
    await engine.stop()
    return {"status": "stopped"}
