"""
TICKET-020 — Attack Prompt Interpreter (Agent 1).
Maps free-form natural language attack prompts to a structured InterpretedAttack
containing attack_type, target_service, intensity, scenario_id, and reasoning.
Uses Literal types to enforce valid scenario IDs at the Pydantic level.
"""
import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from backend.models.threats import AttackType

VALID_SCENARIO_IDS = Literal[
    "account_takeover",
    "transaction_fraud",
    "sql_injection",
    "insider_threat",
    "ddos_attack",
]

VALID_INTENSITIES = Literal["low", "medium", "high"]


class InterpretedAttack(BaseModel):
    """Structured output from the Attack Prompt Interpreter."""
    attack_type: AttackType = Field(..., description="The category of attack being attempted")
    target_service: str = Field(..., description="Primary NovaPay service being targeted")
    intensity: VALID_INTENSITIES = Field(..., description="Attack intensity: low, medium, or high")
    scenario_id: VALID_SCENARIO_IDS = Field(
        ...,
        description="The simulation scenario ID that best matches this attack"
    )
    reasoning: str = Field(..., description="Brief explanation of how the prompt was interpreted")


SYSTEM_PROMPT = """You are the Attack Prompt Interpreter for CyberSentinel, a cybersecurity simulation.

NovaPay is a fictional fintech company with these services:
- auth (login, 2FA, sessions)
- transaction_engine (transfers, payments, balances)
- api_gateway (rate limiting, routing)
- database (customer records, transaction history)
- nginx (HTTP routing, web server)
- firewall (network traffic, port monitoring)

You must map the user's attack prompt to exactly ONE of these scenario IDs:
- account_takeover  → brute force login, credential stuffing, 2FA bypass, session hijacking
- transaction_fraud → fake transactions, money transfers, payment manipulation
- sql_injection      → database injection, malformed queries, table dumps
- insider_threat    → off-hours admin access, bulk data export, PII theft by internal user
- ddos_attack       → traffic flooding, volumetric attack, server overload, botnet

Attack intensity:
- low    → probing, recon, single attempts
- medium → sustained attack, multiple attempts
- high   → aggressive, large-scale, automated

Always pick the CLOSEST matching scenario even if the prompt is vague."""

INTERPRET_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Interpret this attack prompt and return a structured InterpretedAttack:\n\n\"{prompt}\""),
])


class AttackPromptInterpreter:

    def __init__(self, model: str = "gemini-2.5-flash"):
        self._llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY", "placeholder"),
        )

    def interpret(self, prompt: str) -> InterpretedAttack:
        if not prompt or not prompt.strip():
            raise ValueError("Attack prompt cannot be empty")

        structured_llm = self._llm.with_structured_output(InterpretedAttack)
        messages = INTERPRET_PROMPT.format_messages(prompt=prompt)
        return structured_llm.invoke(messages)
