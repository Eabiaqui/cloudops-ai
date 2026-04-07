"""Alert classification pipeline using LangGraph (T4-T8)."""

import json
import re
from typing import Any, TypedDict

import structlog
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from cloudops_ai.config import settings
from cloudops_ai.models.alert import (
    AlertCategory,
    AlertPayload,
    ClassifiedAlert,
    Severity,
)
from cloudops_ai.prompts.classifier import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

log = structlog.get_logger()

_SEVERITY_MAP: dict[str, Severity] = {
    "Sev0": Severity.CRITICAL,
    "Sev1": Severity.CRITICAL,
    "Sev2": Severity.ERROR,
    "Sev3": Severity.WARNING,
    "Sev4": Severity.INFORMATIONAL,
}


# ── State ──────────────────────────────────────────────────────────────────────

class ClassifierState(TypedDict):
    payload: AlertPayload
    classified: ClassifiedAlert | None
    error: str | None


# ── Nodes ──────────────────────────────────────────────────────────────────────

def normalize_alert(state: ClassifierState) -> ClassifierState:
    """T4: Parse raw payload, extract essentials, normalize severity."""
    payload = state["payload"]
    essentials = payload.get_essentials()
    severity_norm = _SEVERITY_MAP.get(essentials.severity, Severity.UNKNOWN)

    state["classified"] = ClassifiedAlert(
        raw_payload=payload,
        essentials=essentials,
        severity_normalized=severity_norm,
    )
    log.info("alert.normalized", alert_rule=essentials.alert_rule, severity=severity_norm)
    return state


def enrich_context(state: ClassifierState) -> ClassifierState:
    """T5: Add context to alert before classification."""
    # MVP: enrichment is basic (just logs). Future: fetch Azure metrics here.
    classified = state["classified"]
    if classified:
        log.info(
            "alert.enriched",
            resource=classified.essentials.affected_resource,
            signal=classified.essentials.signal_type,
        )
    return state


def classify_with_llm(state: ClassifierState) -> ClassifierState:
    """T6-T7: Call Claude Haiku to classify the alert."""
    classified = state["classified"]
    if not classified:
        state["error"] = "No classified alert to process"
        return state

    e = classified.essentials
    user_msg = USER_PROMPT_TEMPLATE.format(
        alert_rule=e.alert_rule or "N/A",
        severity=e.severity,
        signal_type=e.signal_type,
        affected_resource=e.affected_resource_str or "N/A",
        description=e.description or "N/A",
    )

    llm = ChatAnthropic(
        model=settings.classifier_model,
        api_key=settings.anthropic_api_key,
        max_tokens=settings.classifier_max_tokens,
    )

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_msg),
        ])
        raw = response.content
        # Extract JSON from response (handles markdown code blocks too)
        json_match = re.search(r"\{.*\}", str(raw), re.DOTALL)
        if not json_match:
            raise ValueError(f"No JSON found in LLM response: {raw}")

        result: dict[str, Any] = json.loads(json_match.group())
        classified.category = AlertCategory(result.get("category", "unknown"))
        classified.confidence = float(result.get("confidence", 0.0))
        classified.reasoning = result.get("reasoning", "")

        log.info(
            "alert.classified",
            category=classified.category,
            confidence=classified.confidence,
            reasoning=classified.reasoning,
        )
    except Exception as exc:
        log.error("alert.classification_failed", error=str(exc))
        classified.category = AlertCategory.UNKNOWN
        classified.confidence = 0.0
        state["error"] = str(exc)

    state["classified"] = classified
    return state


def route_alert(state: ClassifierState) -> str:
    """T8: Deterministic router — no LLM tokens used here."""
    classified = state["classified"]
    if not classified or classified.category == AlertCategory.UNKNOWN:
        return "unknown"
    return classified.category.value


# ── Graph ──────────────────────────────────────────────────────────────────────

def build_classifier_graph() -> Any:
    graph = StateGraph(ClassifierState)

    graph.add_node("normalize_alert", normalize_alert)
    graph.add_node("enrich_context", enrich_context)
    graph.add_node("classify_with_llm", classify_with_llm)

    graph.set_entry_point("normalize_alert")
    graph.add_edge("normalize_alert", "enrich_context")
    graph.add_edge("enrich_context", "classify_with_llm")
    graph.add_conditional_edges(
        "classify_with_llm",
        route_alert,
        {
            "cpu_pressure": END,
            "memory_pressure": END,
            "disk_io": END,
            "network": END,
            "availability": END,
            "cost_anomaly": END,
            "unknown": END,
        },
    )

    return graph.compile()


# Singleton
classifier_graph = build_classifier_graph()


async def classify_alert(payload: AlertPayload) -> ClassifiedAlert:
    """Entry point: run the classification pipeline."""
    initial_state: ClassifierState = {
        "payload": payload,
        "classified": None,
        "error": None,
    }
    result = await classifier_graph.ainvoke(initial_state)
    classified = result.get("classified")
    if not classified:
        raise RuntimeError(f"Classification failed: {result.get('error')}")
    return classified
