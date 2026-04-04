"""
TICKET-016 — Threat Detector Agent.
Takes a list of ParsedLog objects, queries ChromaDB for relevant CVE/playbook context,
and returns a structured ThreatEvent Pydantic model using with_structured_output().
"""
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from backend.models.logs import ParsedLog
from backend.models.threats import ThreatEvent
from backend.rag.chromadb_client import get_collection

SYSTEM_PROMPT = """You are a threat detection agent for CyberSentinel, a cybersecurity monitoring system
protecting NovaPay — a fictional fintech company.

You receive a batch of structured log entries and relevant CVE/security context from a knowledge base.
Your job is to cross-correlate the logs, identify attack patterns, and produce a structured ThreatEvent.

NovaPay services: auth, transaction_engine, api_gateway, database, nginx, firewall.
Attack types: brute_force, sql_injection, data_exfiltration, ddos, insider_threat, account_takeover, transaction_fraud, unknown.

Be precise. Only flag genuine threats backed by evidence in the logs."""

DETECT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", (
        "Analyze these {log_count} log entries for attack patterns:\n\n"
        "{logs_json}\n\n"
        "Relevant CVE/security context from knowledge base:\n{rag_context}\n\n"
        "Identify the threat and return a structured ThreatEvent."
    )),
])

_RAG_QUERY_RESULTS = 3


class ThreatDetectorAgent:

    def __init__(self, model: str = "gemini-1.5-flash"):
        self._llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY", "placeholder"),
        )

    def detect(self, logs: list[ParsedLog]) -> ThreatEvent:
        if not logs:
            raise ValueError("logs cannot be empty")

        logs_json = json.dumps([log.model_dump(mode="json") for log in logs], indent=2)

        rag_context = self._query_knowledge_base(logs)

        structured_llm = self._llm.with_structured_output(ThreatEvent)
        messages = DETECT_PROMPT.format_messages(
            log_count=len(logs),
            logs_json=logs_json,
            rag_context=rag_context,
        )
        return structured_llm.invoke(messages)

    def _query_knowledge_base(self, logs: list[ParsedLog]) -> str:
        query_text = " ".join(
            f"{log.action or ''} {log.log_type.value}" for log in logs
        ).strip()

        collection = get_collection()
        results = collection.query(
            query_texts=[query_text],
            n_results=_RAG_QUERY_RESULTS,
        )

        documents = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]

        if not documents:
            return "No relevant CVEs found."

        lines = [f"[{cve_id}] {doc}" for cve_id, doc in zip(ids, documents)]
        return "\n".join(lines)
