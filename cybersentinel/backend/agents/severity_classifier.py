"""
TICKET-017 — Severity Classifier Agent.
Takes a ThreatEvent and returns a ScoredThreat with CRITICAL/HIGH/MEDIUM/LOW
severity, a numeric score 0-10, justification, and blast radius.
Uses with_structured_output() — no free-form text between agents.
"""
import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from backend.models.threats import ThreatEvent, ScoredThreat

SYSTEM_PROMPT = """You are a severity classification agent for CyberSentinel, a cybersecurity monitoring system
protecting NovaPay — a fictional fintech company handling real financial transactions.

You receive a structured ThreatEvent and must assign a severity rating with a numeric score.

Severity scale:
- CRITICAL (8.0–10.0): Active breach, data exfiltration, or financial loss occurring now
- HIGH (6.0–7.9): Attack in progress with likely imminent impact
- MEDIUM (4.0–5.9): Suspicious pattern detected, no confirmed breach yet
- LOW (0.0–3.9): Anomalous but likely benign, monitor only

Also identify blast_radius — other NovaPay services likely to be affected.
NovaPay services: auth, transaction_engine, api_gateway, database, nginx, firewall.

Be precise and consistent. Your output feeds directly into the remediation pipeline."""

CLASSIFY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", (
        "Classify the severity of this threat event:\n\n"
        "{threat_json}\n\n"
        "Return a ScoredThreat with severity, score (0.0–10.0), justification, and blast_radius."
    )),
])


class SeverityClassifierAgent:

    def __init__(self, model: str = "gpt-4o-mini"):
        self._llm = ChatOpenAI(
            model=model,
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder"),
        )

    def classify(self, threat: ThreatEvent) -> ScoredThreat:
        threat_json = json.dumps(threat.model_dump(mode="json"), indent=2)

        structured_llm = self._llm.with_structured_output(ScoredThreat)
        messages = CLASSIFY_PROMPT.format_messages(threat_json=threat_json)
        return structured_llm.invoke(messages)
