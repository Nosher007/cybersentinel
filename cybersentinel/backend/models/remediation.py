from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from .threats import ScoredThreat


class RemediationStep(BaseModel):
    """A single actionable remediation step."""
    order: int
    action: str = Field(..., description="What to do")
    detail: str = Field(..., description="How to do it")
    is_immediate: bool = Field(..., description="True = do now, False = long-term hardening")


class RemediationPlan(BaseModel):
    """Full remediation plan produced by the Remediation Agent."""
    plan_id: str = Field(..., description="Unique ID for this remediation plan")
    threat: ScoredThreat
    immediate_steps: List[RemediationStep] = Field(
        ..., description="Steps to take right now to contain the threat"
    )
    hardening_steps: List[RemediationStep] = Field(
        ..., description="Long-term recommendations to prevent recurrence"
    )
    cve_references: List[str] = Field(
        default_factory=list,
        description="Relevant CVE IDs from the knowledge base"
    )
    summary: str = Field(..., description="One paragraph summary of the remediation plan")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
