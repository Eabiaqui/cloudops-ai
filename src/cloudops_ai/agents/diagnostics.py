"""Diagnostics agent — runs after classification for availability + cpu_pressure."""

from typing import TypedDict

import structlog
from langgraph.graph import END, StateGraph

from cloudops_ai.config import settings
from cloudops_ai.llm import call_llm, extract_json_from_response
from cloudops_ai.models.alert import AlertCategory, ClassifiedAlert
from cloudops_ai.models.diagnosis import DiagnosisResult
from cloudops_ai.prompts.diagnostics import (
    AVAILABILITY_USER_TEMPLATE,
    CPU_USER_TEMPLATE,
    SYSTEM_PROMPT,
)
from cloudops_ai.tools.azure_real import (
    get_cpu_metrics,
    get_node_status,
    get_pod_logs,
    get_pod_status,
    get_process_list,
)

log = structlog.get_logger()
log.info("diagnostics.init", llm_backend=settings.llm_backend)

DIAGNOSABLE = {AlertCategory.AVAILABILITY, AlertCategory.CPU_PRESSURE}


# ── State ──────────────────────────────────────────────────────────────────────

class DiagnosticsState(TypedDict):
    classified: ClassifiedAlert
    telemetry: dict                  # raw data gathered from tools
    user_prompt: str                 # assembled prompt for LLM
    result: DiagnosisResult | None
    error: str | None


# ── Nodes ──────────────────────────────────────────────────────────────────────

async def gather_telemetry(state: DiagnosticsState) -> DiagnosticsState:
    """Fetch relevant telemetry based on alert category."""
    classified = state["classified"]
    resource_id = classified.essentials.affected_resource_str
    category = classified.category

    log.info("diagnostics.gathering", category=category, resource=resource_id)

    if category == AlertCategory.CPU_PRESSURE:
        state["telemetry"] = {
            "metrics": get_cpu_metrics(resource_id),
            "processes": get_process_list(resource_id),
        }

    elif category == AlertCategory.AVAILABILITY:
        pods = get_pod_status(resource_id)
        # Find the first crashing pod for log fetch
        crashing = next(
            (p for p in pods if p["status"] not in ("Running", "Completed")),
            pods[0] if pods else {"name": "unknown"},
        )
        state["telemetry"] = {
            "pods": pods,
            "logs": get_pod_logs(resource_id, crashing["name"]),
            "nodes": get_node_status(resource_id),
            "crashing_pod": crashing["name"],
        }

    return state


async def build_prompt(state: DiagnosticsState) -> DiagnosticsState:
    """Assemble the LLM prompt from gathered telemetry."""
    classified = state["classified"]
    telemetry = state["telemetry"]
    resource_id = classified.essentials.affected_resource_str

    if classified.category == AlertCategory.CPU_PRESSURE:
        metrics = telemetry["metrics"]
        processes = "\n".join(
            f"  {p['name']} (pid {p['pid']}): cpu={p['cpu_percent']}% mem={p['mem_mb']}MB"
            for p in telemetry["processes"]
        )
        state["user_prompt"] = CPU_USER_TEMPLATE.format(
            alert_rule=classified.essentials.alert_rule,
            resource_id=resource_id,
            avg=metrics["avg"],
            max=metrics["max"],
            processes=processes,
        )

    elif classified.category == AlertCategory.AVAILABILITY:
        crashing_pods = [
            p for p in telemetry["pods"] if p["status"] not in ("Running", "Completed")
        ]
        pods_str = "\n".join(
            f"  {p['name']}: status={p['status']} restarts={p['restarts']}"
            for p in crashing_pods
        ) or "  No crashing pods detected"

        logs_str = "\n".join(f"  {l}" for l in telemetry["logs"])

        nodes_not_ready = [n for n in telemetry["nodes"] if n["status"] != "Ready"]
        nodes_str = "\n".join(
            f"  {n['name']}: {n['status']} mem_allocatable={n['mem_allocatable']}"
            for n in telemetry["nodes"]
        )

        state["user_prompt"] = AVAILABILITY_USER_TEMPLATE.format(
            alert_rule=classified.essentials.alert_rule,
            resource_id=resource_id,
            pods=pods_str,
            pod_name=telemetry["crashing_pod"],
            logs=logs_str,
            nodes=nodes_str,
        )

    return state


async def call_llm_node(state: DiagnosticsState) -> DiagnosticsState:
    """Call LLM (Anthropic or Ollama) with the assembled prompt."""
    classified = state["classified"]

    try:
        raw = await call_llm(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=state["user_prompt"],
            max_tokens=256,
        )
        llm_out = extract_json_from_response(raw)

        alert_id = classified.essentials.alert_id or classified.essentials.alert_rule
        summary = (
            f"[{classified.category.upper()}] {llm_out.get('diagnosis', '')} "
            f"→ {llm_out.get('suggested_action', '')}"
        )

        state["result"] = DiagnosisResult(
            alert_id=alert_id,
            category=classified.category,
            diagnosis=llm_out.get("diagnosis", ""),
            evidence=llm_out.get("evidence", []),
            suggested_action=llm_out.get("suggested_action", ""),
            confidence=float(llm_out.get("confidence", 0.0)),
            summary=summary,
        )
        log.info(
            "diagnostics.completed",
            alert_id=alert_id,
            diagnosis=state["result"].diagnosis,
            confidence=state["result"].confidence,
            llm_backend=settings.llm_backend,
        )

    except Exception as exc:
        log.error("diagnostics.failed", error=str(exc))
        state["error"] = str(exc)

    return state


# ── Graph ──────────────────────────────────────────────────────────────────────

def _build_graph():
    graph = StateGraph(DiagnosticsState)
    graph.add_node("gather_telemetry", gather_telemetry)
    graph.add_node("build_prompt", build_prompt)
    graph.add_node("call_llm", call_llm_node)
    graph.set_entry_point("gather_telemetry")
    graph.add_edge("gather_telemetry", "build_prompt")
    graph.add_edge("build_prompt", "call_llm")
    graph.add_edge("call_llm", END)
    return graph.compile()


_diagnostics_graph = _build_graph()


async def diagnose(classified: ClassifiedAlert) -> DiagnosisResult | None:
    """Entry point. Returns None if category is not diagnosable."""
    if classified.category not in DIAGNOSABLE:
        return None

    initial: DiagnosticsState = {
        "classified": classified,
        "telemetry": {},
        "user_prompt": "",
        "result": None,
        "error": None,
    }
    result = await _diagnostics_graph.ainvoke(initial)

    if result.get("error") and not result.get("result"):
        raise RuntimeError(f"Diagnostics failed: {result['error']}")

    return result.get("result")
