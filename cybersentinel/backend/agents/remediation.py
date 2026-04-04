"""
TICKET-018 — Remediation Agent.
Takes a ScoredThreat, queries ChromaDB for relevant CVE/playbook context,
and returns a structured RemediationPlan with immediate steps, hardening
recommendations, CVE references, and a summary.
"""
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from backend.models.threats import ScoredThreat
from backend.models.remediation import RemediationPlan
from backend.rag.chromadb_client import get_collection

SYSTEM_PROMPT = """You are a remediation agent for CyberSentinel, a cybersecurity monitoring system
protecting NovaPay — a fictional fintech company handling real financial transactions.

You receive a scored threat and relevant CVE/playbook context from the knowledge base.
Your job is to produce a concrete, actionable RemediationPlan.

Guidelines:
- immediate_steps: actions to take RIGHT NOW to contain the threat (block IPs, revoke sessions, isolate services)
- hardening_steps: long-term recommendations to prevent recurrence (MFA, rate limiting, WAF rules, patching)
- cve_references: list any CVE IDs or OWASP IDs from the knowledge base that are relevant
- summary: one clear paragraph describing what happened and what the response is

NovaPay services: auth, transaction_engine, api_gateway, database, nginx, firewall.
Be specific — reference NovaPay's stack in your steps, not generic advice."""

REMEDIATE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", (
        "Generate a remediation plan for this scored threat:\n\n"
        "{scored_threat_json}\n\n"
        "Relevant CVE/playbook context from knowledge base:\n{rag_context}\n\n"
        "Return a complete RemediationPlan with immediate steps, hardening steps, CVE references, and summary."
    )),
])

_RAG_QUERY_RESULTS = 5


class RemediationAgent:

    def __init__(self, model: str = "gemini-1.5-flash"):
        self._llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY", "placeholder"),
        )

    def remediate(self, scored_threat: ScoredThreat) -> RemediationPlan:
        scored_threat_json = json.dumps(scored_threat.model_dump(mode="json"), indent=2)

        rag_context = self._query_knowledge_base(scored_threat)

        structured_llm = self._llm.with_structured_output(RemediationPlan)
        messages = REMEDIATE_PROMPT.format_messages(
            scored_threat_json=scored_threat_json,
            rag_context=rag_context,
        )
        return structured_llm.invoke(messages)

    def _query_knowledge_base(self, scored_threat: ScoredThreat) -> str:
        attack_type = scored_threat.threat.attack_type.value
        service = scored_threat.threat.affected_service
        severity = scored_threat.severity.value
        query_text = f"{attack_type} {service} {severity} remediation"

        collection = get_collection()
        results = collection.query(
            query_texts=[query_text],
            n_results=_RAG_QUERY_RESULTS,
        )

        documents = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]

        if not documents:
            return "No relevant CVEs or playbooks found."

        lines = [f"[{entry_id}] {doc}" for entry_id, doc in zip(ids, documents)]
        return "\n".join(lines)
