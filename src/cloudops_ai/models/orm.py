"""SQLAlchemy ORM models (multi-tenant)."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Boolean, Float, Integer, ForeignKey, Index, Enum, Date, func, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum

from cloudops_ai.db import Base

# Cross-compatible UUID column (String for SQLite, UUID for PostgreSQL)
UUID_COLUMN = String(36)  # UUID as string for SQLite compatibility

# ============================================================================
# ENUMS
# ============================================================================

class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class AlertStatus(str, enum.Enum):
    NEW = "new"
    RESOLVED = "resolved"
    SILENCED = "silenced"
    ACKNOWLEDGED = "acknowledged"

class AlertCategory(str, enum.Enum):
    CPU_PRESSURE = "cpu_pressure"
    MEMORY_PRESSURE = "memory_pressure"
    DISK_IO = "disk_io"
    NETWORK = "network"
    AVAILABILITY = "availability"
    COST_ANOMALY = "cost_anomaly"
    UNKNOWN = "unknown"

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"

class NotificationStatus(str, enum.Enum):
    SENT = "sent"
    FAILED = "failed"
    DELETED = "deleted"

class AuditAction(str, enum.Enum):
    ALERT_CREATED = "alert_created"
    ALERT_RESOLVED = "alert_resolved"
    CONFIG_UPDATED = "config_updated"
    USER_CREATED = "user_created"
    API_KEY_GENERATED = "api_key_generated"

# ============================================================================
# MODELS
# ============================================================================

class Tenant(Base):
    """Enterprise account."""
    __tablename__ = "tenants"

    id = Column(UUID_COLUMN, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False)
    plan = Column(String(50), default="free")
    stripe_customer_id = Column(String(255), nullable=True)
    language = Column(String(10), default="es")
    timezone = Column(String(50), default="America/Buenos_Aires")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    active = Column(Boolean, default=True)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="tenant", cascade="all, delete-orphan")
    azure_config = relationship("AzureConfig", uselist=False, back_populates="tenant", cascade="all, delete-orphan")
    slack_config = relationship("SlackConfig", uselist=False, back_populates="tenant", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_tenants_api_key", api_key),
    )

class User(Base):
    """User account (tenant member)."""
    __tablename__ = "users"

    id = Column(UUID_COLUMN, primary_key=True, default=lambda: str(uuid4()))
    tenant_id = Column(UUID_COLUMN, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="member")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    active = Column(Boolean, default=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")

    __table_args__ = (
        Index("idx_users_tenant", tenant_id),
        Index("idx_users_email", email),
    )

class AzureConfig(Base):
    """Azure Monitor credentials."""
    __tablename__ = "azure_configs"

    id = Column(UUID_COLUMN, primary_key=True, default=lambda: str(uuid4()))
    tenant_id = Column(UUID_COLUMN, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True)
    subscription_id = Column(String(255), nullable=False)
    client_id = Column(String(255), nullable=False)
    client_secret_encrypted = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="azure_config")

class SlackConfig(Base):
    """Slack workspace integration."""
    __tablename__ = "slack_configs"

    id = Column(UUID_COLUMN, primary_key=True, default=lambda: str(uuid4()))
    tenant_id = Column(UUID_COLUMN, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True)
    workspace_id = Column(String(255), nullable=False)
    webhook_url = Column(String(500), nullable=False)
    channel_id = Column(String(255), nullable=True)
    channel_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    enabled = Column(Boolean, default=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="slack_config")

class Alert(Base):
    """Alert from monitoring system."""
    __tablename__ = "alerts"

    id = Column(UUID_COLUMN, primary_key=True, default=lambda: str(uuid4()))
    tenant_id = Column(UUID_COLUMN, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    alert_id_external = Column(String(255), nullable=True)
    rule_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=True)
    confidence = Column(Float, default=0.0)
    severity = Column(String(50), nullable=True)
    payload_raw = Column(JSON, nullable=False)  # JSONB for PostgreSQL, JSON for SQLite
    status = Column(String(50), default="new")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="alerts")
    diagnosis = relationship("Diagnosis", uselist=False, back_populates="alert", cascade="all, delete-orphan")
    slack_notification = relationship("SlackNotification", uselist=False, back_populates="alert", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_alerts_tenant_date", tenant_id, "created_at"),
        Index("idx_alerts_category", tenant_id, category),
        Index("idx_alerts_status", tenant_id, status),
    )

class Diagnosis(Base):
    """AI diagnosis of an alert."""
    __tablename__ = "diagnoses"

    id = Column(UUID_COLUMN, primary_key=True, default=lambda: str(uuid4()))
    tenant_id = Column(UUID_COLUMN, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    alert_id = Column(UUID_COLUMN, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False)
    diagnosis = Column(String, nullable=False)
    evidence = Column(JSON, default=list, nullable=False)  # JSONB for PostgreSQL, JSON for SQLite
    suggested_action = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    model_used = Column(String(50), default="claude-haiku")
    tokens_used = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    alert = relationship("Alert", back_populates="diagnosis")

    __table_args__ = (
        Index("idx_diagnoses_tenant_alert", tenant_id, alert_id),
    )

class SlackNotification(Base):
    """Track Slack notifications sent."""
    __tablename__ = "slack_notifications"

    id = Column(UUID_COLUMN, primary_key=True, default=lambda: str(uuid4()))
    tenant_id = Column(UUID_COLUMN, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    alert_id = Column(UUID_COLUMN, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False)
    slack_ts = Column(String(255), nullable=True)
    status = Column(String(50), default="sent")
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    alert = relationship("Alert", back_populates="slack_notification")

    __table_args__ = (
        Index("idx_slack_notif_tenant", tenant_id, "created_at"),
    )

class APIKey(Base):
    """API key for webhook authentication."""
    __tablename__ = "api_keys"

    id = Column(UUID_COLUMN, primary_key=True, default=lambda: str(uuid4()))
    tenant_id = Column(UUID_COLUMN, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_api_keys_tenant", tenant_id),
        Index("idx_api_keys_hash", key_hash),
    )

class AuditLog(Base):
    """Audit trail for compliance."""
    __tablename__ = "audit_logs"

    id = Column(UUID_COLUMN, primary_key=True, default=lambda: str(uuid4()))
    tenant_id = Column(UUID_COLUMN, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID_COLUMN, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(255), nullable=True)
    details = Column(JSON, nullable=True)  # JSONB for PostgreSQL, JSON for SQLite
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_audit_logs_tenant", tenant_id, "created_at"),
        Index("idx_audit_logs_action", tenant_id, action),
    )

class Usage(Base):
    """Monthly usage tracking for billing."""
    __tablename__ = "usage"

    id = Column(UUID_COLUMN, primary_key=True, default=lambda: str(uuid4()))
    tenant_id = Column(UUID_COLUMN, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True)
    alerts_processed = Column(Integer, default=0)
    diagnoses_generated = Column(Integer, default=0)
    month_year = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_usage_tenant_month", tenant_id, month_year),
    )
