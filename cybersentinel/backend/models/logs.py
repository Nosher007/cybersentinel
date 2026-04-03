from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class LogType(str, Enum):
    AUTH = "auth"
    NGINX = "nginx"
    FIREWALL = "firewall"
    DATABASE = "database"
    API = "api"


class RawLog(BaseModel):
    """A raw, unprocessed log string from the simulation engine."""
    raw: str = Field(..., description="The raw log line as emitted by the simulation")
    log_type: LogType = Field(..., description="Which NovaPay service produced this log")
    received_at: datetime = Field(default_factory=datetime.utcnow)
    scenario_id: Optional[str] = Field(None, description="Which attack scenario this belongs to")


class ParsedLog(BaseModel):
    """Structured log produced by the Log Parser Agent from a RawLog."""
    raw: str = Field(..., description="Original raw log string")
    log_type: LogType
    timestamp: datetime
    source_ip: Optional[str] = None
    user: Optional[str] = None
    action: Optional[str] = None
    status_code: Optional[int] = None
    endpoint: Optional[str] = None
    message: Optional[str] = None
    extra: dict = Field(default_factory=dict, description="Any additional extracted fields")
    scenario_id: Optional[str] = None
