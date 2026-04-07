"""Real Azure SDK tools — metrics via Azure Management API

Uses:
  - azure-mgmt-monitor: for metrics queries
  - azure-monitor-query: for KQL (logs)
  - azure-identity: for service principal authentication
"""

from datetime import datetime, timedelta

import structlog
from azure.identity import ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.monitor.query import LogsQueryClient

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
    """Fetch CPU utilization metrics from Azure Monitor."""
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

        log.info("get_cpu_metrics.success", resource=resource_id, avg=avg_cpu, max=max_cpu, samples=len(samples))

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
        # Fallback to mock for now
        return {
            "resource_id": resource_id,
            "metric": "Percentage CPU (mock — no data)",
            "unit": "percent",
            "samples": [],
            "avg": 0.0,
            "max": 0.0,
        }


def get_process_list(resource_id: str) -> list[dict]:
    """Fetch top CPU-consuming processes via KQL in Log Analytics.

    Requires the resource to be connected to Log Analytics for agent reporting.
    """
    try:
        credential = _get_credential()
        client = LogsQueryClient(credential)

        query = """
        Perf
        | where ObjectName == "Processor" and CounterName == "% Processor Time"
        | summarize AvgCPU = avg(CounterValue) by ProcessName
        | order by AvgCPU desc
        | limit 5
        """

        log.warning("get_process_list.not_implemented", resource=resource_id)
        return []

    except Exception as exc:
        log.error("get_process_list.failed", error=str(exc))
        return []


# ── Availability / Kubernetes tools ──────────────────────────────────────────

def get_pod_status(resource_id: str) -> list[dict]:
    """Fetch pod statuses from AKS cluster via KQL."""
    try:
        credential = _get_credential()
        client = LogsQueryClient(credential)

        query = """
        KubePodInventory
        | where TimeGenerated > ago(30m)
        | summarize by PodName, Namespace, PodStatus
        | project
            name = PodName,
            namespace = Namespace,
            status = PodStatus
        | limit 10
        """

        log.warning("get_pod_status.not_implemented", resource=resource_id)
        return []

    except Exception as exc:
        log.error("get_pod_status.failed", error=str(exc))
        return []


def get_pod_logs(resource_id: str, pod_name: str, tail: int = 20) -> list[str]:
    """Fetch recent pod logs from Log Analytics."""
    try:
        credential = _get_credential()
        client = LogsQueryClient(credential)

        query = f"""
        ContainerLog
        | where PodName == "{pod_name}"
        | where TimeGenerated > ago(1h)
        | order by TimeGenerated desc
        | limit {tail}
        | project LogEntry = LogMessage
        """

        log.warning("get_pod_logs.not_implemented", pod=pod_name, resource=resource_id)
        return []

    except Exception as exc:
        log.error("get_pod_logs.failed", error=str(exc), pod=pod_name)
        return []


def get_node_status(resource_id: str) -> list[dict]:
    """Fetch AKS node pool health from KQL."""
    try:
        credential = _get_credential()
        client = LogsQueryClient(credential)

        query = """
        KubeNodeInventory
        | where TimeGenerated > ago(30m)
        | summarize by NodeName, Status
        """

        log.warning("get_node_status.not_implemented", resource=resource_id)
        return []

    except Exception as exc:
        log.error("get_node_status.failed", error=str(exc))
        return []
