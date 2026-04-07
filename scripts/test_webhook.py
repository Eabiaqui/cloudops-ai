#!/usr/bin/env python3
"""Send a test alert payload to the local webhook endpoint."""

import httpx
import json
import sys

BASE_URL = "http://localhost:8000"

SAMPLE_ALERTS = [
    {
        "name": "High CPU",
        "payload": {
            "schemaId": "azureMonitorCommonAlertSchema",
            "data": {
                "essentials": {
                    "alertId": "/subscriptions/sub-123/alerts/cpu-001",
                    "alertRule": "High CPU Usage - vm-web-01",
                    "severity": "Sev2",
                    "signalType": "Metric",
                    "monitorCondition": "Fired",
                    "monitoringService": "Platform",
                    "alertTargetIDs": "/subscriptions/sub-123/resourceGroups/rg-prod/providers/Microsoft.Compute/virtualMachines/vm-web-01",
                    "firedDateTime": "2024-01-15T10:30:00Z",
                    "description": "CPU percentage above 90% for 5 minutes on vm-web-01",
                }
            },
        },
    },
    {
        "name": "Pod CrashLoopBackOff",
        "payload": {
            "schemaId": "azureMonitorCommonAlertSchema",
            "data": {
                "essentials": {
                    "alertId": "/subscriptions/sub-123/alerts/k8s-001",
                    "alertRule": "AKS Pod CrashLoopBackOff",
                    "severity": "Sev1",
                    "signalType": "Log",
                    "monitorCondition": "Fired",
                    "monitoringService": "Log Analytics",
                    "alertTargetIDs": "/subscriptions/sub-123/resourceGroups/rg-prod/providers/Microsoft.ContainerService/managedClusters/aks-prod",
                    "firedDateTime": "2024-01-15T11:00:00Z",
                    "description": "Pod api-gateway-7d9f8b-xkp2q is in CrashLoopBackOff state",
                }
            },
        },
    },
    {
        "name": "Cost Spike",
        "payload": {
            "schemaId": "azureMonitorCommonAlertSchema",
            "data": {
                "essentials": {
                    "alertId": "/subscriptions/sub-123/alerts/cost-001",
                    "alertRule": "Monthly Budget 80% Threshold",
                    "severity": "Sev3",
                    "signalType": "Activity Log",
                    "monitorCondition": "Fired",
                    "monitoringService": "Cost Management",
                    "alertTargetIDs": "/subscriptions/sub-123",
                    "firedDateTime": "2024-01-15T09:00:00Z",
                    "description": "Subscription spend has reached 80% of monthly budget ($4,000 of $5,000)",
                }
            },
        },
    },
]


def main() -> None:
    alert_name = sys.argv[1] if len(sys.argv) > 1 else None

    with httpx.Client(timeout=30) as client:
        # Health check
        resp = client.get(f"{BASE_URL}/health")
        print(f"Health: {resp.json()}\n")

        alerts_to_send = SAMPLE_ALERTS
        if alert_name:
            alerts_to_send = [a for a in SAMPLE_ALERTS if alert_name.lower() in a["name"].lower()]

        for alert in alerts_to_send:
            print(f"--- Sending: {alert['name']} ---")
            resp = client.post(f"{BASE_URL}/alert", json=alert["payload"])
            print(f"Status: {resp.status_code}")
            print(json.dumps(resp.json(), indent=2))
            print()


if __name__ == "__main__":
    main()
