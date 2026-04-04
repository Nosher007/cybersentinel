"""
TICKET-019 — LangGraph Orchestrator.
StateGraph wiring LogParser → ThreatDetector → SeverityClassifier → Remediation.
Each node receives the full AgentState and returns a partial update.
Errors are caught per-node and stored in state["error"] rather than crashing.
"""
from typing import Optional
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END

from backend.agents.log_parser import LogParserAgent
from backend.agents.threat_detector import ThreatDetectorAgent
from backend.agents.severity_classifier import SeverityClassifierAgent
from backend.agents.remediation import RemediationAgent
from backend.models.logs import ParsedLog, LogType
from backend.models.threats import ThreatEvent, ScoredThreat
from backend.models.remediation import RemediationPlan


class AgentState(TypedDict):
    raw_logs: list                          # list of (raw_log_str, log_type_str) tuples
    parsed_logs: Optional[list]             # list[ParsedLog]
    threat_event: Optional[ThreatEvent]
    scored_threat: Optional[ScoredThreat]
    remediation_plan: Optional[RemediationPlan]
    error: Optional[str]


# ── Node functions ────────────────────────────────────────────────────────────

def parse_logs_node(state: AgentState) -> dict:
    if not state.get("raw_logs"):
        return {"error": "No logs provided to pipeline", "parsed_logs": None}
    try:
        agent = LogParserAgent()
        log_tuples = [
            (raw, LogType(log_type)) for raw, log_type in state["raw_logs"]
        ]
        parsed = agent.parse_batch(log_tuples)
        return {"parsed_logs": parsed}
    except Exception as exc:
        return {"error": f"LogParser failed: {exc}", "parsed_logs": None}


def detect_threat_node(state: AgentState) -> dict:
    if state.get("error"):
        return {}
    try:
        agent = ThreatDetectorAgent()
        threat = agent.detect(state["parsed_logs"])
        return {"threat_event": threat}
    except Exception as exc:
        return {"error": f"ThreatDetector failed: {exc}", "threat_event": None}


def classify_severity_node(state: AgentState) -> dict:
    if state.get("error"):
        return {}
    try:
        agent = SeverityClassifierAgent()
        scored = agent.classify(state["threat_event"])
        return {"scored_threat": scored}
    except Exception as exc:
        return {"error": f"SeverityClassifier failed: {exc}", "scored_threat": None}


def remediate_node(state: AgentState) -> dict:
    if state.get("error"):
        return {}
    try:
        agent = RemediationAgent()
        plan = agent.remediate(state["scored_threat"])
        return {"remediation_plan": plan}
    except Exception as exc:
        return {"error": f"RemediationAgent failed: {exc}", "remediation_plan": None}


# ── Graph assembly ────────────────────────────────────────────────────────────

def build_pipeline():
    graph = StateGraph(AgentState)

    graph.add_node("parse_logs", parse_logs_node)
    graph.add_node("detect_threat", detect_threat_node)
    graph.add_node("classify_severity", classify_severity_node)
    graph.add_node("remediate", remediate_node)

    graph.set_entry_point("parse_logs")
    graph.add_edge("parse_logs", "detect_threat")
    graph.add_edge("detect_threat", "classify_severity")
    graph.add_edge("classify_severity", "remediate")
    graph.add_edge("remediate", END)

    return graph.compile()
