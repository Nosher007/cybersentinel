"""
TICKET-027 — WebSocket router (updated).
Streams simulation logs to all connected clients.
When simulation ends, runs the agent pipeline and broadcasts results.
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Tracks all active WebSocket connections."""

    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict):
        disconnected = []
        for ws in self.active:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)


manager = ConnectionManager()


try:
    from backend.agents.orchestrator import build_pipeline
    from backend.routers.threats import threat_store
except ModuleNotFoundError:
    from agents.orchestrator import build_pipeline
    from routers.threats import threat_store


def _run_agent_pipeline(collected_logs: list[tuple[str, str]]) -> dict | None:
    """Synchronous — runs in thread pool via run_in_executor."""
    if not collected_logs:
        return None

    try:
        pipeline = build_pipeline()
        result = pipeline.invoke({"raw_logs": collected_logs})

        if result.get("error"):
            return {"error": result["error"]}

        plan = result["remediation_plan"]
        threat = result["scored_threat"]

        threat_record = {
            "attack_type": threat.threat.attack_type.value,
            "affected_service": threat.threat.affected_service,
            "severity": threat.severity.value,
            "score": threat.score,
            "justification": threat.justification,
            "blast_radius": threat.blast_radius,
        }
        threat_store.append(threat_record)

        return {
            "threat": threat_record,
            "remediation": {
                "plan_id": plan.plan_id,
                "summary": plan.summary,
                "immediate_steps": [
                    {"order": s.order, "action": s.action, "detail": s.detail}
                    for s in plan.immediate_steps
                ],
                "hardening_steps": [
                    {"order": s.order, "action": s.action, "detail": s.detail}
                    for s in plan.hardening_steps
                ],
                "cve_references": plan.cve_references,
            },
        }
    except Exception as exc:
        return {"error": f"Agent pipeline failed: {exc}"}


async def broadcast_from_engine():
    """
    Background task: reads logs from engine queue, broadcasts to WS clients,
    collects logs, and runs the agent pipeline when simulation ends.
    """
    from backend.routers.attack import engine

    collected_logs: list[tuple[str, str]] = []

    while True:
        try:
            log = await asyncio.wait_for(engine.queue.get(), timeout=1.0)

            # Broadcast raw log to all WS clients
            await manager.broadcast({"type": "log", "log": log})

            # Collect for agent pipeline (store as (raw_log, log_type) tuple)
            # log is a string — default to AUTH type for collector; agents parse it
            collected_logs.append((log, "auth"))

            # When simulation ends, run the pipeline
            if not engine.is_running and engine.queue.empty():
                await manager.broadcast({"type": "status", "message": "simulation_complete"})

                if collected_logs:
                    loop = asyncio.get_event_loop()
                    logs_snapshot = list(collected_logs)
                    collected_logs.clear()

                    result = await loop.run_in_executor(
                        None, _run_agent_pipeline, logs_snapshot
                    )

                    if result:
                        if "error" in result:
                            await manager.broadcast({"type": "pipeline_error", "error": result["error"]})
                        else:
                            await manager.broadcast({"type": "threat_detected", "data": result["threat"]})
                            await manager.broadcast({"type": "remediation_plan", "data": result["remediation"]})

        except asyncio.TimeoutError:
            # Reset collected logs if engine stopped between polls
            if not engine.is_running and collected_logs:
                collected_logs.clear()
            continue
        except asyncio.CancelledError:
            break


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            await ws.send_text(json.dumps({"type": "ack", "message": data}))
    except WebSocketDisconnect:
        manager.disconnect(ws)
