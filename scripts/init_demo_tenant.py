#!/usr/bin/env python3
"""Initialize demo tenant for MVP (run once)."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env before importing modules
load_dotenv(Path(__file__).parent.parent / ".env")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cloudops_ai.db import engine, SessionLocal, init_db
from cloudops_ai.models.orm import Tenant

# Demo tenant UUID (fixed, known)
DEMO_TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"
DEMO_TENANT_API_KEY = "demo-azure-monitor-key-do-not-rotate"

def init_demo():
    """Create demo tenant if not exists."""
    # Initialize DB tables
    init_db()
    
    session = SessionLocal()
    
    try:
        # Check if demo tenant already exists
        existing = session.query(Tenant).filter(Tenant.id == DEMO_TENANT_ID).first()
        if existing:
            print(f"✅ Demo tenant already exists: {DEMO_TENANT_ID}")
            return
        
        # Create demo tenant
        demo_tenant = Tenant(
            id=DEMO_TENANT_ID,
            name="Demo - CloudOps AI",
            api_key=DEMO_TENANT_API_KEY,
            plan="free",
            language="es",
            timezone="America/Buenos_Aires",
            active=True,
        )
        session.add(demo_tenant)
        session.commit()
        
        print(f"✅ Demo tenant created:")
        print(f"   ID: {DEMO_TENANT_ID}")
        print(f"   Name: Demo - CloudOps AI")
        print(f"   API Key: {DEMO_TENANT_API_KEY}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    init_demo()
