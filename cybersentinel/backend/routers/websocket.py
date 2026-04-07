"""
WebSocket router — staged pipeline broadcasting.
Fires the AI pipeline after 5 logs and broadcasts results after EACH agent,
so the threat card appears mid-attack and remediation follows shortly after.
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Fire pipeline after this many logs are collected (lower = earlier AI response)
PIPELINE_TRIGGER_THRESHOLD = 5


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
    from backend.agents.log_parser import LogParserAgent
    from backend.agents.threat_detector import ThreatDetectorAgent
    from backend.agents.severity_classifier import SeverityClassifierAgent
    from backend.agents.remediation import RemediationAgent
    from backend.models.logs import LogType
    from backend.routers.threats import threat_store
    from backend.simulation.phase_metrics import get_metrics_for_tag, HEALTHY_METRICS
except ModuleNotFoundError:
    from agents.log_parser import LogParserAgent
    from agents.threat_detector import ThreatDetectorAgent
    from agents.severity_classifier import SeverityClassifierAgent
    from agents.remediation import RemediationAgent
    from models.logs import LogType
    from routers.threats import threat_store
    from simulation.phase_metrics import get_metrics_for_tag, HEALTHY_METRICS


import re as _re
_LOG_TAG_RE = _re.compile(r'\[([A-Z0-9_-]+)\]')

_SERVICE_TAG_TO_LOG_TYPE = {
    "AUTH": "auth",
    "NGINX": "nginx",
    "API-GW": "api",
    "FIREWALL": "firewall",
    "DB": "database",
    "TXN-ENGINE": "api",
    "COMPLIANCE": "database",
    "BOTNET": "firewall",
}


def _detect_log_type(log_line: str) -> str:
    for tag in _LOG_TAG_RE.findall(log_line):
        log_type = _SERVICE_TAG_TO_LOG_TYPE.get(tag)
        if log_type:
            return log_type
    return "auth"


def _parse_logs(logs: list[tuple[str, str]]) -> list:
    agent = LogParserAgent()
    log_tuples = [(raw, LogType(lt)) for raw, lt in logs]
    return agent.parse_batch(log_tuples)


def _detect_threat(parsed_logs: list):
    agent = ThreatDetectorAgent()
    return agent.detect(parsed_logs)


def _classify_severity(threat_event):
    agent = SeverityClassifierAgent()
    return agent.classify(threat_event)


def _remediate(scored_threat):
    agent = RemediationAgent()
    return agent.remediate(scored_threat)


async def _run_pipeline_staged(collected_logs: list[tuple[str, str]]):
    """
    Run agents one at a time in a thread executor and broadcast after each stage.
    This gives the frontend a live play-by-play:
      - Threat card appears as soon as ThreatDetector finishes
      - Severity badge updates when Classifier finishes
      - Remediation steps populate when Remediation finishes
    """
    if not collected_logs:
        return

    loop = asyncio.get_event_loop()

    try:
        # Stage 1: Parse logs (silent — just prep for next stage)
        parsed_logs = await loop.run_in_executor(None, _parse_logs, collected_logs)
        if not parsed_logs:
            await manager.broadcast({"type": "pipeline_error", "error": "Log parsing returned no results"})
            return

        # Stage 2: Detect threat → broadcast immediately so threat card appears
        threat_event = await loop.run_in_executor(None, _detect_threat, parsed_logs)
        if not threat_event:
            await manager.broadcast({"type": "pipeline_error", "error": "Threat detection returned no result"})
            return

        # Stage 3: Classify severity → broadcast severity update
        scored_threat = await loop.run_in_executor(None, _classify_severity, threat_event)
        if not scored_threat:
            await manager.broadcast({"type": "pipeline_error", "error": "Severity classification failed"})
            return

        # Build the threat record and broadcast (threat card now has full data)
        threat_record = {
            "attack_type": scored_threat.threat.attack_type.value,
            "affected_service": scored_threat.threat.affected_service,
            "severity": scored_threat.severity.value,
            "score": scored_threat.score,
            "justification": scored_threat.justification,
            "blast_radius": scored_threat.blast_radius,
        }
        threat_store.append(threat_record)
        await manager.broadcast({"type": "threat_detected", "data": threat_record})

        # Stage 4: Remediate → broadcast steps (these populate one by one on frontend)
        plan = await loop.run_in_executor(None, _remediate, scored_threat)
        if plan:
            await manager.broadcast({
                "type": "remediation_plan",
                "data": {
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
            })

    except Exception as exc:
        import traceback
        traceback.print_exc()
        await manager.broadcast({"type": "pipeline_error", "error": f"Pipeline failed: {exc}"})


async def broadcast_from_engine():
    """
    Background task: reads logs from engine queue, broadcasts to WS clients.
    After PIPELINE_TRIGGER_THRESHOLD logs, fires the staged AI pipeline so
    analysis appears mid-attack.
    """
    from backend.routers.attack import engine

    collected_logs: list[tuple[str, str]] = []
    pipeline_fired = False
    pipeline_task = None

    while True:
        try:
            log = await asyncio.wait_for(engine.queue.get(), timeout=1.0)

            # Broadcast raw log to all WS clients immediately
            await manager.broadcast({"type": "log", "log": log})

            # Broadcast metric update based on log tag
            match = _LOG_TAG_RE.search(log)
            if match:
                tag = match.group(1)
                metrics = get_metrics_for_tag(tag)
                if metrics:
                    await manager.broadcast({"type": "metric_update", "data": metrics})

            # Collect for pipeline
            collected_logs.append((log, _detect_log_type(log)))

            # Fire pipeline mid-attack once threshold is reached
            if not pipeline_fired and len(collected_logs) >= PIPELINE_TRIGGER_THRESHOLD:
                pipeline_fired = True
                logs_snapshot = list(collected_logs)
                print(f"[PIPELINE] Firing staged pipeline mid-attack with {len(logs_snapshot)} logs", flush=True)
                pipeline_task = asyncio.create_task(_run_pipeline_staged(logs_snapshot))

            # Simulation ended while reading a log
            if not engine.is_running and engine.queue.empty():
                await manager.broadcast({"type": "status", "message": "simulation_complete"})
                await manager.broadcast({"type": "metric_update", "data": HEALTHY_METRICS})

                # If pipeline hasn't fired yet (very short simulation), fire now
                if not pipeline_fired and collected_logs:
                    logs_snapshot = list(collected_logs)
                    print(f"[PIPELINE] Firing staged pipeline post-simulation with {len(logs_snapshot)} logs", flush=True)
                    await _run_pipeline_staged(logs_snapshot)

                # Wait for in-flight pipeline to finish
                if pipeline_task and not pipeline_task.done():
                    await pipeline_task

                # Reset state for next attack
                collected_logs.clear()
                pipeline_fired = False
                pipeline_task = None

        except asyncio.TimeoutError:
            # Engine stopped between queue polls
            if not engine.is_running and collected_logs:
                await manager.broadcast({"type": "status", "message": "simulation_complete"})
                await manager.broadcast({"type": "metric_update", "data": HEALTHY_METRICS})

                if not pipeline_fired:
                    logs_snapshot = list(collected_logs)
                    print(f"[PIPELINE] Firing staged pipeline (timeout path) with {len(logs_snapshot)} logs", flush=True)
                    await _run_pipeline_staged(logs_snapshot)

                if pipeline_task and not pipeline_task.done():
                    await pipeline_task

                collected_logs.clear()
                pipeline_fired = False
                pipeline_task = None
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
