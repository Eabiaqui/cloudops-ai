"""FastAPI application — webhook endpoint (T3)."""

import hashlib
import hmac
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

from cloudops_ai.agents.classifier import classify_alert
from cloudops_ai.agents.diagnostics import diagnose, DIAGNOSABLE
from cloudops_ai.config import settings
from cloudops_ai.logging import configure_logging
from cloudops_ai.models.alert import AlertPayload

log = structlog.get_logger()

# In-memory store for recent alerts (MVP — swap for SQLite later)
_recent_alerts: list[dict[str, Any]] = []
MAX_RECENT = 100


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    configure_logging(settings.log_level)
    log.info("cloudops_ai.started", env=settings.app_env, port=settings.app_port)
    yield
    log.info("cloudops_ai.stopped")


app = FastAPI(
    title="CloudOps AI",
    version="0.1.0",
    description="Autonomous NOC alert classifier",
    lifespan=lifespan,
)


def _verify_webhook_secret(body: bytes, signature: str | None) -> None:
    """Optional HMAC verification for Azure Monitor webhook."""
    if not signature or settings.app_env == "development":
        return
    expected = hmac.new(
        settings.webhook_secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(f"sha256={expected}", signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.get("/alerts/recent")
async def recent_alerts() -> list[dict[str, Any]]:
    return _recent_alerts[-MAX_RECENT:]


@app.post("/alert", status_code=status.HTTP_202_ACCEPTED)
async def receive_alert(
    request: Request,
    x_webhook_signature: str | None = Header(default=None),
) -> JSONResponse:
    """Receive Azure Monitor Action Group webhook and classify the alert."""
    body = await request.body()
    _verify_webhook_secret(body, x_webhook_signature)

    try:
        raw_data = await request.json()
        payload = AlertPayload.model_validate(raw_data)
    except Exception as exc:
        log.warning("alert.parse_failed", error=str(exc))
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    classified = await classify_alert(payload)

    result: dict = {
        "alert_rule": classified.essentials.alert_rule,
        "category": classified.category,
        "confidence": classified.confidence,
        "severity": classified.severity_normalized,
        "reasoning": classified.reasoning,
        "processed_at": classified.processed_at.isoformat(),
        "diagnosis": None,
    }

    if classified.category in DIAGNOSABLE:
        diagnosis = await diagnose(classified)
        if diagnosis:
            result["diagnosis"] = {
                "diagnosis": diagnosis.diagnosis,
                "evidence": diagnosis.evidence,
                "suggested_action": diagnosis.suggested_action,
                "confidence": diagnosis.confidence,
                "summary": diagnosis.summary,
            }

    _recent_alerts.append(result)
    log.info("alert.processed", alert_rule=result["alert_rule"], category=result["category"])
    return JSONResponse(content=result, status_code=status.HTTP_202_ACCEPTED)
