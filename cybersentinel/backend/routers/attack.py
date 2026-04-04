"""
TICKET-027 — Attack router (updated).
POST /attack: interprets natural language prompt → starts simulation → triggers agent pipeline
POST /stop:   stops the running scenario
"""
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from simulation.engine import SimulationEngine, SCENARIO_REGISTRY

try:
    from backend.agents.prompt_interpreter import AttackPromptInterpreter
except ModuleNotFoundError:
    from agents.prompt_interpreter import AttackPromptInterpreter

router = APIRouter()

engine = SimulationEngine()


class AttackRequest(BaseModel):
    prompt: str


@router.post("/attack")
async def start_attack(req: AttackRequest):
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt cannot be empty")

    if engine.is_running:
        raise HTTPException(
            status_code=409,
            detail=f"Scenario '{engine.current_scenario_id}' is already running. POST /stop first."
        )

    interpreter = AttackPromptInterpreter()
    interpreted = await asyncio.get_event_loop().run_in_executor(
        None, interpreter.interpret, req.prompt
    )

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
