"""Azure Monitor alert payload models (T2)."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Severity(StrEnum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFORMATIONAL = "informational"
    UNKNOWN = "unknown"


class AlertCategory(StrEnum):
    CPU_PRESSURE = "cpu_pressure"
    MEMORY_PRESSURE = "memory_pressure"
    DISK_IO = "disk_io"
    NETWORK = "network"
    AVAILABILITY = "availability"
    COST_ANOMALY = "cost_anomaly"
    UNKNOWN = "unknown"


class AlertEssentials(BaseModel):
    """Parsed from Azure Monitor common alert schema."""

    alert_id: str = Field(alias="alertId", default="")
    alert_rule: str = Field(alias="alertRule", default="")
    severity: str = Field(default="Sev3")
    signal_type: str = Field(alias="signalType", default="Metric")
    monitor_condition: str = Field(alias="monitorCondition", default="Fired")
    monitoring_service: str = Field(alias="monitoringService", default="")
    affected_resource: str | list[str] = Field(alias="alertTargetIDs", default="")

    @property
    def affected_resource_str(self) -> str:
        if isinstance(self.affected_resource, list):
            return self.affected_resource[0] if self.affected_resource else ""
        return self.affected_resource
    fired_time: str = Field(alias="firedDateTime", default="")
    description: str = Field(default="")

    model_config = {"populate_by_name": True}


class AlertPayload(BaseModel):
    """Raw webhook payload from Azure Monitor Action Group."""

    schema_id: str = Field(alias="schemaId", default="")
    data: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    def get_essentials(self) -> AlertEssentials:
        essentials_data = self.data.get("essentials", {})
        return AlertEssentials.model_validate(essentials_data)


class ClassifiedAlert(BaseModel):
    """Output of the classification pipeline."""

    raw_payload: AlertPayload
    essentials: AlertEssentials
    category: AlertCategory = AlertCategory.UNKNOWN
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    reasoning: str = ""
    severity_normalized: Severity = Severity.UNKNOWN
    processed_at: datetime = Field(default_factory=datetime.utcnow)
