from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from .logs import ParsedLog


class AttackType(str, Enum):
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    DATA_EXFILTRATION = "data_exfiltration"
    DDOS = "ddos"
    INSIDER_THREAT = "insider_threat"
    ACCOUNT_TAKEOVER = "account_takeover"
    TRANSACTION_FRAUD = "transaction_fraud"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ThreatEvent(BaseModel):
    """A detected threat pattern produced by the Threat Detector Agent."""
    threat_id: str = Field(..., description="Unique ID for this threat event")
    attack_type: AttackType
    affected_service: str = Field(..., description="NovaPay service under attack")
    evidence_logs: List[ParsedLog] = Field(..., description="Logs that triggered this threat")
    description: str = Field(..., description="Human-readable threat description")
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    scenario_id: Optional[str] = None


class ScoredThreat(BaseModel):
    """A threat event with severity score, produced by the Severity Classifier Agent."""
    threat: ThreatEvent
    severity: Severity
    score: float = Field(..., ge=0.0, le=10.0, description="Numeric severity score 0-10")
    justification: str = Field(..., description="Why this severity was assigned")
    blast_radius: List[str] = Field(
        default_factory=list,
        description="Other NovaPay services potentially affected"
    )
    classified_at: datetime = Field(default_factory=datetime.utcnow)
