"""Diagnosis output model."""

from datetime import datetime
from pydantic import BaseModel, Field


class DiagnosisResult(BaseModel):
    alert_id: str
    category: str
    diagnosis: str
    evidence: list[str]
    suggested_action: str
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    diagnosed_at: datetime = Field(default_factory=datetime.utcnow)
