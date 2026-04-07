"""Azure tool mocks — same interface as future Azure SDK implementations.

To switch to real Azure in Fase 3:
  1. Create tools/azure_real.py implementing the same functions
  2. Change the import in agents/diagnostics.py: from .azure_real import ...
  3. Done. No other changes needed.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta


# ── CPU tools ─────────────────────────────────────────────────────────────────

def get_cpu_metrics(resource_id: str, minutes: int = 30) -> dict:
    """Return CPU utilization samples for the last N minutes."""
    now = datetime.utcnow()
    samples = [
        {
            "timestamp": (now - timedelta(minutes=minutes - i)).isoformat(),
            "cpu_percent": round(random.uniform(85, 99), 1),
        }
        for i in range(0, minutes, 5)
    ]
    return {
        "resource_id": resource_id,
        "metric": "Percentage CPU",
        "unit": "percent",
        "samples": samples,
        "avg": round(sum(s["cpu_percent"] for s in samples) / len(samples), 1),
        "max": max(s["cpu_percent"] for s in samples),
    }


def get_process_list(resource_id: str) -> list[dict]:
    """Return top CPU-consuming processes on the resource."""
    return [
        {"pid": 1842, "name": "java",        "cpu_percent": 78.2, "mem_mb": 2048},
        {"pid": 2201, "name": "python",       "cpu_percent": 12.4, "mem_mb": 512},
        {"pid": 991,  "name": "nginx",        "cpu_percent": 3.1,  "mem_mb": 128},
        {"pid": 1,    "name": "systemd",      "cpu_percent": 0.1,  "mem_mb": 8},
    ]


# ── Availability / Kubernetes tools ──────────────────────────────────────────

def get_pod_status(resource_id: str) -> list[dict]:
    """Return pod statuses for the AKS cluster."""
    return [
        {
            "name": "api-gateway-7d9f8b-xkp2q",
            "namespace": "prod",
            "status": "CrashLoopBackOff",
            "restarts": 7,
            "last_restart": (datetime.utcnow() - timedelta(minutes=3)).isoformat(),
            "image": "myacr.azurecr.io/api-gateway:v2.3.1",
        },
        {
            "name": "api-gateway-7d9f8b-mn9rt",
            "namespace": "prod",
            "status": "Running",
            "restarts": 0,
            "last_restart": None,
            "image": "myacr.azurecr.io/api-gateway:v2.3.1",
        },
        {
            "name": "redis-0",
            "namespace": "prod",
            "status": "Running",
            "restarts": 0,
            "last_restart": None,
            "image": "redis:7-alpine",
        },
    ]


def get_pod_logs(resource_id: str, pod_name: str, tail: int = 20) -> list[str]:
    """Return recent log lines for a specific pod."""
    return [
        "2026-04-07T01:00:01Z INFO  Starting api-gateway v2.3.1",
        "2026-04-07T01:00:02Z INFO  Connecting to database...",
        "2026-04-07T01:00:03Z ERROR Cannot allocate memory: java.lang.OutOfMemoryError: Java heap space",
        "2026-04-07T01:00:03Z ERROR   at com.cloudops.gateway.Router.init(Router.java:142)",
        "2026-04-07T01:00:03Z ERROR   at com.cloudops.gateway.App.main(App.java:58)",
        "2026-04-07T01:00:03Z FATAL Process terminated with exit code 137 (OOMKilled)",
    ]


def get_node_status(resource_id: str) -> list[dict]:
    """Return AKS node pool health."""
    return [
        {"name": "aks-nodepool1-001", "status": "Ready",    "cpu_capacity": "4",  "mem_capacity": "8Gi",  "mem_allocatable": "7.2Gi"},
        {"name": "aks-nodepool1-002", "status": "Ready",    "cpu_capacity": "4",  "mem_capacity": "8Gi",  "mem_allocatable": "7.4Gi"},
        {"name": "aks-nodepool1-003", "status": "NotReady", "cpu_capacity": "4",  "mem_capacity": "8Gi",  "mem_allocatable": "0Gi"},
    ]
