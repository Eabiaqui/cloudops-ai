"""FastAPI v1 endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID, uuid4
import secrets
from datetime import datetime
import asyncio

from cloudops_ai.db import get_db
from cloudops_ai.models.orm import User, Tenant, APIKey, Alert, Diagnosis, AuditLog, AuditAction
from cloudops_ai.auth import hash_password, verify_password, create_access_token, decode_token, hash_api_key, verify_api_key
from cloudops_ai.agents.classifier import classify_alert
from cloudops_ai.agents.diagnostics import diagnose
from cloudops_ai.models.alert import AlertPayload
from cloudops_ai.integrations.slack_notifier import send_alert_to_slack
from cloudops_ai.tools.azure_mock import get_inventory as get_azure_inventory
import asyncio
import csv
import io

# Demo tenant UUID (MVP: all alerts go here)
DEMO_TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

router = APIRouter(prefix="/api/v1", tags=["v1"])

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@router.post("/auth/signup")
def signup(email: str, password: str, tenant_name: str, db: Session = Depends(get_db)):
    """Create new user in demo tenant (MVP: all users share same tenant)."""
    # Get demo tenant
    tenant = db.query(Tenant).filter(Tenant.id == DEMO_TENANT_ID).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Demo tenant not initialized. Run: python3 scripts/init_demo_tenant.py"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
    # Create user in demo tenant
    user = User(
        tenant_id=tenant.id,
        email=email,
        password_hash=hash_password(password),
        role="admin",
    )
    db.add(user)
    db.commit()

    # Convert string UUID to UUID object for token creation
    tenant_uuid = UUID(tenant.id) if isinstance(tenant.id, str) else tenant.id
    user_uuid = UUID(user.id) if isinstance(user.id, str) else user.id
    token = create_access_token(tenant_id=tenant_uuid, user_id=user_uuid)
    return {
        "access_token": token,
        "tenant_id": str(tenant.id),
        "user_id": str(user.id),
        "tenant_name": "Demo - CloudOps AI",
    }

@router.post("/auth/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    """Login user."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Convert string UUID to UUID object for token creation
    tenant_uuid = UUID(user.tenant_id) if isinstance(user.tenant_id, str) else user.tenant_id
    user_uuid = UUID(user.id) if isinstance(user.id, str) else user.id
    token = create_access_token(tenant_id=tenant_uuid, user_id=user_uuid)
    return {
        "access_token": token,
        "tenant_id": str(user.tenant_id),
        "user_id": str(user.id),
    }

# ============================================================================
# HELPER: Get current tenant from JWT or API Key
# ============================================================================

def get_current_tenant(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Extract tenant_id from Authorization header (Bearer token or API key)."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization")

    try:
        scheme, credentials = authorization.split()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

    if scheme.lower() == "bearer":
        # JWT token
        token_data = decode_token(credentials)
        if not token_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return token_data.tenant_id

    elif scheme.lower() == "api_key":
        # API key
        api_key_record = db.query(APIKey).filter(APIKey.key_hash == credentials).first()
        if not api_key_record:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
        api_key_record.last_used_at = ...  # Would update last_used_at
        return str(api_key_record.tenant_id)

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scheme")

# ============================================================================
# WEBHOOK: Receive alerts
# ============================================================================

async def _run_diagnostics_background(alert_id: str, classified):
    """Run diagnostics in background after alert is stored."""
    # Give DB a moment to settle
    await asyncio.sleep(0.5)
    
    try:
        diagnosis_result = await diagnose(classified)
        if diagnosis_result:
            # Store diagnosis in background
            from cloudops_ai.db import SessionLocal
            db = SessionLocal()
            try:
                diag = Diagnosis(
                    id=str(uuid4()),
                    tenant_id=DEMO_TENANT_ID,
                    alert_id=alert_id,
                    diagnosis=diagnosis_result.diagnosis,
                    evidence=diagnosis_result.evidence,
                    suggested_action=diagnosis_result.suggested_action,
                    confidence=diagnosis_result.confidence,
                )
                db.add(diag)
                db.commit()
            finally:
                db.close()
    except Exception as e:
        pass  # Log would happen in diagnose()


@router.post("/webhooks/alert", status_code=status.HTTP_202_ACCEPTED)
async def receive_alert(
    payload: dict,
    db: Session = Depends(get_db),
):
    """Receive alert from Azure Monitor webhook (no auth needed, always goes to demo tenant)."""
    try:
        alert_payload = AlertPayload.model_validate(payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # Classify alert
    classified = await classify_alert(alert_payload)

    # Store in demo tenant (MVP: all Azure alerts go here)
    alert = Alert(
        id=str(uuid4()),  # Generate UUID as string for SQLite
        tenant_id=DEMO_TENANT_ID,  # Always demo tenant
        alert_id_external=classified.essentials.alert_id,
        rule_name=classified.essentials.alert_rule,
        category=classified.category,
        confidence=classified.confidence,
        severity=classified.severity_normalized,
        payload_raw=classified.raw_payload.model_dump(),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # Run diagnostics in background (don't block webhook response)
    asyncio.create_task(_run_diagnostics_background(str(alert.id), classified))

    return {
        "alert_id": str(alert.id),
        "category": classified.category,
        "confidence": classified.confidence,
        "severity": classified.severity_normalized,
    }

# ============================================================================
# ALERTS: List and get
# ============================================================================

@router.get("/alerts")
def list_alerts(
    tenant_id: str = Depends(get_current_tenant),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List recent alerts for tenant."""
    alerts = db.query(Alert).filter(
        Alert.tenant_id == tenant_id  # tenant_id is already a string from SQLite
    ).order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": len(alerts),
        "alerts": [
            {
                "id": str(a.id),
                "rule_name": a.rule_name,
                "category": a.category,
                "severity": a.severity,
                "created_at": a.created_at.isoformat(),
                "status": a.status,
            }
            for a in alerts
        ]
    }

@router.get("/alerts/{alert_id}")
def get_alert(
    alert_id: str,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Get single alert with diagnosis."""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,  # String UUID from SQLite
        Alert.tenant_id == tenant_id,  # String UUID from SQLite
    ).first()

    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    # Flatten diagnosis into top-level response
    response = {
        "id": str(alert.id),
        "rule_name": alert.rule_name,
        "category": alert.category,
        "severity": alert.severity,
        "created_at": alert.created_at.isoformat(),
        "status": alert.status,
    }

    # Add diagnosis fields directly to response
    if alert.diagnosis:
        response["diagnosis"] = alert.diagnosis.diagnosis
        response["evidence"] = alert.diagnosis.evidence
        response["suggested_action"] = alert.diagnosis.suggested_action
        response["confidence"] = alert.diagnosis.confidence

    return response

# ============================================================================
# ALERT ACTIONS
# ============================================================================

@router.patch("/alerts/{alert_id}")
def update_alert(
    alert_id: str,
    alert_status: str = Query(...),
    tenant_id: str = Depends(get_current_tenant),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Update alert status (resolved, acknowledged, escalated)."""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == tenant_id,
    ).first()

    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    # Extract user_id from JWT token if available
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        token_data = decode_token(authorization.split(" ")[1])
        if token_data:
            user_id = token_data.user_id

    alert.status = alert_status
    if alert_status == "resolved":
        alert.resolved_at = datetime.utcnow()
    db.commit()

    # Log audit trail
    audit = AuditLog(
        id=str(uuid4()),
        tenant_id=tenant_id,
        user_id=user_id,
        action=AuditAction.ALERT_RESOLVED if alert_status == "resolved" else "alert_acknowledged",
        resource_type="alert",
        resource_id=alert_id,
        details={"new_status": alert_status, "previous_status": alert.status},
    )
    db.add(audit)
    db.commit()

    return {
        "id": str(alert.id),
        "status": alert.status,
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
    }

# ============================================================================
# INVENTORY & EXPORT
# ============================================================================

@router.get("/inventory")
def get_inventory(
    tenant_id: str = Depends(get_current_tenant),
    subscription_id: Optional[str] = None,
    resource_group: Optional[str] = None,
    resource_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get resource inventory from Azure (mock or real)."""
    resources = get_azure_inventory(
        subscription_id=subscription_id,
        resource_group=resource_group,
        resource_type=resource_type,
    )
    
    # Enrich with alert counts
    alerts = db.query(Alert).filter(Alert.tenant_id == tenant_id).all()
    alert_counts = {}
    for alert in alerts:
        payload = alert.payload_raw if isinstance(alert.payload_raw, dict) else {}
        resource = payload.get("resource", "unknown")
        if resource not in alert_counts:
            alert_counts[resource] = 0
        alert_counts[resource] += 1
    
    for resource in resources:
        resource["alert_count"] = alert_counts.get(resource.get("name"), 0)
    
    return {"resources": resources, "total": len(resources)}

@router.get("/inventory/export")
def export_inventory(
    format: str = "json",
    subscription_id: Optional[str] = None,
    resource_group: Optional[str] = None,
    resource_type: Optional[str] = None,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Export inventory as JSON or CSV."""
    resources = get_azure_inventory(
        subscription_id=subscription_id,
        resource_group=resource_group,
        resource_type=resource_type,
    )
    
    # Enrich with alert counts
    alerts = db.query(Alert).filter(Alert.tenant_id == tenant_id).all()
    alert_counts = {}
    for alert in alerts:
        payload = alert.payload_raw if isinstance(alert.payload_raw, dict) else {}
        resource = payload.get("resource", "unknown")
        if resource not in alert_counts:
            alert_counts[resource] = 0
        alert_counts[resource] += 1
    
    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Name", "Type", "Subscription", "Resource Group", "Status", "Location", "Alert Count"])
        for resource in resources:
            writer.writerow([
                resource.get("name", ""),
                resource.get("type", ""),
                resource.get("subscription_id", ""),
                resource.get("resource_group", ""),
                resource.get("status", ""),
                resource.get("location", ""),
                alert_counts.get(resource.get("name"), 0),
            ])
        return {"format": "csv", "data": output.getvalue(), "filename": "inventory.csv"}
    
    return {"format": "json", "resources": resources, "total": len(resources)}

# ============================================================================
# SECURITY SCAN
# ============================================================================

@router.post("/security-scan")
def run_security_scan(
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Run security scan for deprecated/risky resources."""
    alerts = db.query(Alert).filter(Alert.tenant_id == tenant_id).all()
    
    scan_results = {
        "deprecated_resources": [],
        "security_risks": [],
        "recommendations": [],
        "scan_timestamp": datetime.utcnow().isoformat(),
    }
    
    # Check for deprecated patterns
    deprecated_keywords = ["old", "legacy", "v1", "deprecated"]
    for alert in alerts:
        payload = alert.payload_raw if isinstance(alert.payload_raw, dict) else {}
        resource_name = payload.get("resource", "")
        if any(keyword in resource_name.lower() for keyword in deprecated_keywords):
            scan_results["deprecated_resources"].append({
                "resource": resource_name,
                "reason": "Matches deprecated naming pattern",
                "severity": "warning",
            })
    
    # Security risks from alerts
    critical_alerts = [a for a in alerts if a.severity == "critical"]
    if len(critical_alerts) > 3:
        scan_results["security_risks"].append({
            "type": "high_alert_volume",
            "description": f"{len(critical_alerts)} critical alerts active",
            "risk_level": "high",
        })
    
    # Recommendations
    if scan_results["deprecated_resources"]:
        scan_results["recommendations"].append(
            "Plan migration away from deprecated resources"
        )
    if scan_results["security_risks"]:
        scan_results["recommendations"].append(
            "Investigate and remediate critical alerts immediately"
        )
    if len(alerts) > 10:
        scan_results["recommendations"].append(
            "Consider implementing alert fatigue reduction strategies"
        )
    
    return scan_results

# ============================================================================
# API KEYS
# ============================================================================

@router.post("/api-keys")
def generate_api_key(
    description: Optional[str] = None,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Generate new API key for tenant."""
    api_key_plain = secrets.token_urlsafe(32)
    api_key_hash = hash_api_key(api_key_plain)

    api_key = APIKey(
        tenant_id=UUID(tenant_id),
        key_hash=api_key_hash,
        description=description,
    )
    db.add(api_key)
    db.commit()

    return {
        "api_key": api_key_plain,  # Only show once
        "key_id": str(api_key.id),
        "created_at": api_key.created_at.isoformat(),
    }

# ============================================================================
# HEALTH
# ============================================================================

@router.get("/health")
def health():
    """Health check."""
    return {"status": "ok", "version": "0.1.0"}


# ─── INVENTORY ───────────────────────────────────────────
from .tools.azure_mock_inventory import get_inventory, get_subscriptions, get_resource_groups
import csv, io
from fastapi.responses import StreamingResponse

@router.get("/inventory")
async def list_inventory(
    subscription: str = None,
    resource_group: str = None,
    resource_type: str = None,
    tenant=Depends(get_current_tenant)
):
    resources = get_inventory(subscription, resource_group, resource_type)
    return {
        "total": len(resources),
        "subscriptions": get_subscriptions(),
        "resource_groups": get_resource_groups(subscription),
        "resources": resources
    }

@router.get("/inventory/export")
async def export_inventory(
    format: str = "csv",
    subscription: str = None,
    resource_group: str = None,
    resource_type: str = None,
    tenant=Depends(get_current_tenant)
):
    resources = get_inventory(subscription, resource_group, resource_type)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["name","type","subscription_id","resource_group","status","location"])
        writer.writeheader()
        for r in resources:
            writer.writerow({k: r.get(k,"") for k in ["name","type","subscription_id","resource_group","status","location"]})
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=qhunu-inventory-{date_str}.csv"}
        )

    return {"error": "format must be csv"}
