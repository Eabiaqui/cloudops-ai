"""FastAPI v1 endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import secrets

from cloudops_ai.db import get_db
from cloudops_ai.models.orm import User, Tenant, APIKey, Alert, Diagnosis
from cloudops_ai.auth import hash_password, verify_password, create_access_token, decode_token, hash_api_key, verify_api_key
from cloudops_ai.agents.classifier import classify_alert
from cloudops_ai.models.alert import AlertPayload

router = APIRouter(prefix="/api/v1", tags=["v1"])

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@router.post("/auth/signup")
def signup(email: str, password: str, tenant_name: str, db: Session = Depends(get_db)):
    """Create new tenant and admin user."""
    # Create tenant
    tenant = Tenant(
        name=tenant_name,
        api_key=secrets.token_urlsafe(32),
    )
    db.add(tenant)
    db.flush()

    # Create admin user
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
        "api_key": tenant.api_key,
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

@router.post("/webhooks/alert", status_code=status.HTTP_202_ACCEPTED)
async def receive_alert(
    payload: dict,
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Receive alert from Azure Monitor webhook."""
    try:
        alert_payload = AlertPayload.model_validate(payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # Classify alert
    classified = await classify_alert(alert_payload)

    # Store in DB
    alert = Alert(
        id=str(UUID()),  # Generate UUID as string for SQLite
        tenant_id=tenant_id,  # Already a string from Depends
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

    diagnosis_data = None
    if alert.diagnosis:
        diagnosis_data = {
            "diagnosis": alert.diagnosis.diagnosis,
            "evidence": alert.diagnosis.evidence,
            "suggested_action": alert.diagnosis.suggested_action,
            "confidence": alert.diagnosis.confidence,
        }

    return {
        "id": str(alert.id),
        "rule_name": alert.rule_name,
        "category": alert.category,
        "severity": alert.severity,
        "created_at": alert.created_at.isoformat(),
        "status": alert.status,
        "diagnosis": diagnosis_data,
    }

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
