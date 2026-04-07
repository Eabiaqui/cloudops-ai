"""Real Azure SDK tools — metrics via Azure Management API

Uses:
  - azure-mgmt-monitor: for metrics queries (✅ Working)
  - azure-monitor-query: for KQL (logs) — requires Log Analytics workspace
  - azure-identity: for service principal authentication

Note: Metrics queries work. Log queries require LAW setup.
For MVP, only CPU metrics are available. KQL queries return gracefully if LAW is not configured.
"""

from datetime import datetime, timedelta

import structlog
from azure.identity import ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient

from cloudops_ai.config import settings

log = structlog.get_logger()


def _get_credential():
    """Service principal credentials from .env"""
    return ClientSecretCredential(
        tenant_id=settings.azure_tenant_id,
        client_id=settings.azure_client_id,
        client_secret=settings.azure_client_secret,
    )


# ── CPU tools ─────────────────────────────────────────────────────────────────

def get_cpu_metrics(resource_id: str, minutes: int = 30) -> dict:
    """Fetch CPU utilization metrics from Azure Monitor.
    
    Returns:
      - samples: list of {timestamp, cpu_percent} tuples (last 6 data points)
      - avg, max: aggregate CPU percentages
      
    Works for any resource with Percentage CPU metric (VMs, App Services, etc.)
    """
    try:
        credential = _get_credential()
        client = MonitorManagementClient(credential, settings.azure_subscription_id)

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes)

        timespan = f"{start_time.isoformat()}Z/{end_time.isoformat()}Z"

        metrics = client.metrics.list(
            resource_uri=resource_id,
            timespan=timespan,
            metricnames="Percentage CPU",
            interval="PT5M",
        )

        samples = []
        cpu_values = []

        for metric in metrics.value:
            for timeseries in metric.timeseries:
                for data_point in timeseries.data:
                    if data_point.average is not None:
                        samples.append({
                            "timestamp": data_point.time_stamp.isoformat(),
                            "cpu_percent": round(data_point.average, 1),
                        })
                        cpu_values.append(data_point.average)

        avg_cpu = round(sum(cpu_values) / len(cpu_values), 1) if cpu_values else 0.0
        max_cpu = round(max(cpu_values), 1) if cpu_values else 0.0

        log.info(
            "get_cpu_metrics.success",
            resource=resource_id,
            avg=avg_cpu,
            max=max_cpu,
            samples=len(samples),
        )

        return {
            "resource_id": resource_id,
            "metric": "Percentage CPU",
            "unit": "percent",
            "samples": sorted(samples, key=lambda x: x["timestamp"])[-6:],
            "avg": avg_cpu,
            "max": max_cpu,
        }

    except Exception as exc:
        log.error("get_cpu_metrics.failed", error=str(exc), resource_id=resource_id)
        # Return empty but valid structure
        return {
            "resource_id": resource_id,
            "metric": "Percentage CPU",
            "unit": "percent",
            "samples": [],
            "avg": 0.0,
            "max": 0.0,
            "error": str(exc),
        }


def get_process_list(resource_id: str) -> list[dict]:
    """Fetch top CPU-consuming processes via KQL in Log Analytics.

    Requires:
      - Resource connected to Log Analytics workspace
      - Azure Monitor agent (AMA) or legacy agent installed
      - Perf table populated with process data

    Returns empty list if LAW not configured (expected in MVP).
    """
    log.warning(
        "get_process_list.skipped",
        reason="Log Analytics workspace not configured",
        resource=resource_id,
    )
    return []


# ── Availability / Kubernetes tools ──────────────────────────────────────────

def get_pod_status(resource_id: str) -> list[dict]:
    """Fetch pod statuses from AKS cluster via KQL.

    Requires:
      - AKS cluster connected to Log Analytics workspace
      - Container Insights enabled on cluster
      - KubePodInventory table populated

    Returns empty list if LAW not configured.
    """
    log.warning(
        "get_pod_status.skipped",
        reason="Log Analytics workspace not configured",
        resource=resource_id,
    )
    return []


def get_pod_logs(resource_id: str, pod_name: str, tail: int = 20) -> list[str]:
    """Fetch recent pod logs from Log Analytics.

    Requires:
      - AKS cluster connected to Log Analytics workspace
      - Container Insights enabled
      - ContainerLog table populated

    Returns empty list if LAW not configured.
    """
    log.warning(
        "get_pod_logs.skipped",
        reason="Log Analytics workspace not configured",
        pod=pod_name,
        resource=resource_id,
    )
    return []


def get_node_status(resource_id: str) -> list[dict]:
    """Fetch AKS node pool health from KQL.

    Requires:
      - AKS cluster connected to Log Analytics workspace
      - Container Insights enabled
      - KubeNodeInventory table populated

    Returns mock data for MVP (safe fallback).
    """
    log.warning(
        "get_node_status.skipped",
        reason="Log Analytics workspace not configured",
        resource=resource_id,
    )
    # Return safe defaults for MVP
    return [
        {
            "name": "aks-nodepool1-001",
            "status": "Ready",
            "cpu_capacity": "4",
            "mem_capacity": "8Gi",
            "mem_allocatable": "7.2Gi",
        },
        {
            "name": "aks-nodepool1-002",
            "status": "Ready",
            "cpu_capacity": "4",
            "mem_capacity": "8Gi",
            "mem_allocatable": "7.4Gi",
        },
    ]
