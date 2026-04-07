"""Tests for alert data models."""

import pytest
from cloudops_ai.models.alert import AlertPayload, AlertCategory, Severity


SAMPLE_PAYLOAD = {
    "schemaId": "azureMonitorCommonAlertSchema",
    "data": {
        "essentials": {
            "alertId": "/subscriptions/sub-123/alerts/alert-456",
            "alertRule": "High CPU Usage",
            "severity": "Sev2",
            "signalType": "Metric",
            "monitorCondition": "Fired",
            "monitoringService": "Platform",
            "alertTargetIDs": ["/subscriptions/sub-123/resourceGroups/rg-prod/providers/Microsoft.Compute/virtualMachines/vm-web-01"],
            "firedDateTime": "2024-01-15T10:30:00Z",
            "description": "CPU percentage above 90% for 5 minutes",
        }
    },
}


def test_parse_alert_payload():
    payload = AlertPayload.model_validate(SAMPLE_PAYLOAD)
    assert payload.schema_id == "azureMonitorCommonAlertSchema"


def test_get_essentials():
    payload = AlertPayload.model_validate(SAMPLE_PAYLOAD)
    essentials = payload.get_essentials()
    assert essentials.alert_rule == "High CPU Usage"
    assert essentials.severity == "Sev2"


def test_alert_category_enum():
    assert AlertCategory("cpu_pressure") == AlertCategory.CPU_PRESSURE
    assert AlertCategory("unknown") == AlertCategory.UNKNOWN


def test_severity_enum():
    assert Severity("critical") == Severity.CRITICAL
