# Week 3: Product Design — Complete Spec

**Timeline:** This week (2026-04-14 to 2026-04-20)  
**Target audience:** LATAM DevOps leads (Spanish, affordable pricing)  
**Deliverables:** Figma + spec doc + API spec  

---

## 1. USER FLOWS (Complete)

### Flow 1: Signup + Setup (First-time user)

```
User lands on landing page
  ↓
"Start free" → Email signup
  ↓
Confirm email
  ↓
Choose cloud: Azure / AWS / GCP
  ↓
Input credentials (subscription ID, client ID, secret)
  ↓
"Copy this webhook URL"
  ↓
Auto-test: "Webhook working ✓"
  ↓
Dashboard (empty, waiting for alerts)
  ↓
"Integrate Slack?" → OAuth flow
  ↓
Dashboard ready
```

**Time to productive:** 5 minutes  
**Language:** Spanish UI, English SDK docs (for code snippets)

---

### Flow 2: See Alerts (Daily driver)

```
User logs in
  ↓
Dashboard shows:
  - Last 24 hours: 47 alerts
  - Last 7 days: 312 alerts
  - Unresolved: 3 critical
  
Table displays:
  - Time | Rule | Category | Severity | Diagnosis | Status
  
User can:
  - Filter by: date range, category, severity, rule
  - Sort by: newest, oldest, severity
  - Export: CSV
```

**Refresh rate:** Real-time (WebSocket) or 5-second polling

---

### Flow 3: View Alert Detail

```
User clicks alert in table
  ↓
Slide-out panel (right side)
  
Shows:
  - Alert rule name
  - Time fired
  - Raw payload (JSON)
  - Category (badge)
  - Diagnosis:
    * Root cause (1 sentence)
    * Evidence (bullet points)
    * Suggested action (concrete step)
    * Confidence (%)
  - Actions:
    * "Copy diagnosis"
    * "Silence this rule for 24h"
    * "Escalate"
    * "Mark resolved"
  - Slack notification sent? (yes/no + timestamp)
```

---

### Flow 4: Setup Slack

```
From settings → Integrations
  ↓
"Connect Slack" button
  ↓
OAuth dialog (Slack)
  ↓
Select channel: #incidents (or custom)
  ↓
"Test notification" → sends sample alert
  ↓
"Connected ✓"
  
Now:
  - Every critical alert → Slack post with diagnosis
  - User can click "View in CloudOps" button
```

---

### Flow 5: Manage API Keys

```
From settings → API Keys
  ↓
"Generate new key"
  ↓
Modal shows: [copy key] [revoke]
  ↓
User stores safely
  ↓
Can use for: direct API calls (future)
```

---

## 2. FIGMA WIREFRAMES (Spec)

### Screen 1: Landing Page

```
┌─────────────────────────────────────────┐
│  CloudOps AI                    Login   │
├─────────────────────────────────────────┤
│                                         │
│  HEADLINE (large):                      │
│  "Diagnostica alertas automáticamente   │
│   con IA. De horas a minutos."          │
│                                         │
│  SUBHEADING:                            │
│  "Reduce investigation time 70%."       │
│                                         │
│  [CTA: "Comienza gratis"]               │
│                                         │
├─────────────────────────────────────────┤
│  ¿Por qué CloudOps?                     │
│  ✓ Diagnóstico automático               │
│  ✓ Multi-cloud (Azure, AWS, GCP)        │
│  ✓ 1,000 alerts/mes gratis              │
│                                         │
│  Precios:                               │
│  Free: $0 (1k alerts)                   │
│  Pro: $99/mes (10k alerts) — LATAM     │
│  Enterprise: custom                     │
│                                         │
└─────────────────────────────────────────┘
```

**Notes:**
- Copy en español
- Pricing en USD (but show ARS equivalent with exchange rate)
- Simple, clean, no fluff

---

### Screen 2: Login

```
┌─────────────────────────────────────────┐
│  CloudOps AI                            │
├─────────────────────────────────────────┤
│                                         │
│  Login                                  │
│                                         │
│  Email: [____________]                  │
│  Password: [____________]               │
│                                         │
│  [Log in]                               │
│                                         │
│  ¿No tienes cuenta?                     │
│  [Sign up gratis]                       │
│                                         │
└─────────────────────────────────────────┘
```

---

### Screen 3: Setup Wizard (3 steps)

```
STEP 1: Choose cloud
┌─────────────────────────────────────────┐
│  Setup CloudOps                         │
│  Step 1 of 3: Select your cloud         │
├─────────────────────────────────────────┤
│                                         │
│  [Azure]    [AWS]    [GCP]              │
│                                         │
│  [Next]                                 │
└─────────────────────────────────────────┘

STEP 2: Add credentials
┌─────────────────────────────────────────┐
│  Setup CloudOps                         │
│  Step 2 of 3: Connect Azure             │
├─────────────────────────────────────────┤
│                                         │
│  Subscription ID:                       │
│  [________________________]              │
│                                         │
│  Client ID:                             │
│  [________________________]              │
│                                         │
│  Client Secret:                         │
│  [________________________]              │
│                                         │
│  [Help: How to find these?] (docs link) │
│                                         │
│  [Test connection] → "✓ Working"        │
│  [Next]                                 │
└─────────────────────────────────────────┘

STEP 3: Copy webhook
┌─────────────────────────────────────────┐
│  Setup CloudOps                         │
│  Step 3 of 3: Configure Azure Monitor   │
├─────────────────────────────────────────┤
│                                         │
│  Your webhook URL:                      │
│  https://api.cloudopsai.com/webhook     │
│  [Copy] [✓ Copied]                      │
│                                         │
│  Paste this into Azure Monitor          │
│  Action Group webhook URL               │
│                                         │
│  [I've configured it]                   │
│  [Skip for now]                         │
│                                         │
│  [Done → Go to Dashboard]               │
└─────────────────────────────────────────┘
```

---

### Screen 4: Dashboard (Main)

```
┌──────────────────────────────────────────────────────────┐
│ CloudOps AI          [User]  [Settings]  [Logout]        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Dashboard                                                │
│                                                          │
│ Last 24h: 47 alerts  |  Last 7d: 312 alerts            │
│ Unresolved: 3 critical  |  Avg MTTR: 18 min            │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Filters: [Date range ▼]  [Category ▼]  [Severity ▼]   │
│                                                          │
│ Sort: [Newest ▼]                                         │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ TIME         │ RULE              │ CAT  │ SEV  │ DIAG   │
├──────────────────────────────────────────────────────────┤
│ 14:32:01     │ High CPU vm-web01 │ CPU  │ !    │ Java.. │
│ 14:15:45     │ Pod Crash api-gw  │ AVAIL│ !!!  │ OOM... │
│ 13:42:12     │ Cost Spike prod   │ COST │ !    │ Spike. │
│ 13:15:00     │ Disk Full db-1    │ DISK │ !!   │ Purge..│
│                                                          │
│ [Load more...]                                           │
└──────────────────────────────────────────────────────────┘
```

---

### Screen 5: Alert Detail Panel

```
┌─────────────────────────────────────┐
│ Alert Detail                    [x] │
├─────────────────────────────────────┤
│                                     │
│ Pod CrashLoopBackOff                │
│ 2026-04-14 14:15:45 UTC             │
│ Category: Availability [CRITICAL]   │
│                                     │
├─────────────────────────────────────┤
│ DIAGNÓSTICO                         │
│                                     │
│ Root cause:                         │
│ Java app OOMKilled durante init     │
│                                     │
│ Evidence:                           │
│ • Exit code 137 (container killed)  │
│ • 7 restart attempts sin cambios    │
│ • Pod logs: OutOfMemoryError        │
│ • Node tiene 7.4Gi disponible       │
│                                     │
│ Suggested action:                   │
│ Aumenta pod memory limit a 768Mi    │
│ en el deployment YAML               │
│                                     │
│ Confidence: 95%                     │
│                                     │
├─────────────────────────────────────┤
│ [Copy diagnosis]  [Slack posted ✓]  │
│ [Silence 24h]     [Mark resolved]   │
│ [Escalate]                          │
└─────────────────────────────────────┘
```

---

### Screen 6: Settings

```
┌─────────────────────────────────────┐
│ Settings                            │
├─────────────────────────────────────┤
│                                     │
│ Cloud Configuration                 │
│ Azure (subscription-123)  [Edit]    │
│ Status: ✓ Connected                 │
│                                     │
│ Slack Integration                   │
│ #incidents  [Connected] [Disconnect]│
│                                     │
│ API Keys                            │
│ [Generate new key]                  │
│ • key_abc123 created 2026-04-07     │
│   [Revoke]                          │
│                                     │
│ Billing                             │
│ Plan: Free (1,000 alerts/month)     │
│ Usage this month: 847 alerts (85%)  │
│ [Upgrade to Pro]                    │
│                                     │
│ Account                             │
│ Email: edu@example.com              │
│ Password: [Change]                  │
│ [Delete account]                    │
│                                     │
└─────────────────────────────────────┘
```

---

## 3. DATABASE SCHEMA (Final)

```sql
-- Multi-tenant
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE,
    plan ENUM('free', 'pro', 'enterprise'),
    stripe_customer_id VARCHAR(255),
    language ENUM('es', 'en') DEFAULT 'es',
    timezone VARCHAR(50) DEFAULT 'America/Buenos_Aires',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    role ENUM('admin', 'member') DEFAULT 'member',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cloud configs (encrypted at rest)
CREATE TABLE azure_configs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    subscription_id VARCHAR(255) NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    client_secret_encrypted VARCHAR(500) NOT NULL, -- AES-256
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id) -- One config per tenant
);

CREATE TABLE slack_configs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    webhook_url VARCHAR(500) NOT NULL ENCRYPTED,
    channel_id VARCHAR(255),
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Core alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    alert_id_external VARCHAR(255), -- Azure's alert ID
    rule_name VARCHAR(255) NOT NULL,
    category VARCHAR(50), -- cpu_pressure, availability, etc.
    confidence FLOAT,
    severity VARCHAR(50), -- critical, error, warning, info
    payload_raw JSONB, -- Full alert payload
    status ENUM('new', 'resolved', 'silenced') DEFAULT 'new',
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    INDEX (tenant_id, created_at DESC)
);

-- Diagnoses (AI results)
CREATE TABLE diagnoses (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    diagnosis TEXT NOT NULL,
    evidence TEXT[] (array of strings),
    suggested_action TEXT,
    confidence FLOAT,
    model_used VARCHAR(50), -- 'claude-haiku', future: gpt-4
    created_at TIMESTAMP DEFAULT NOW()
);

-- Slack notifications tracking
CREATE TABLE slack_notifications (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    slack_ts VARCHAR(255), -- For threaded updates
    status ENUM('sent', 'failed') DEFAULT 'sent',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit logs (compliance)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100), -- 'alert_resolved', 'config_updated', etc.
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX (tenant_id, created_at DESC)
);

-- Usage tracking (for billing)
CREATE TABLE usage (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    alerts_processed INT DEFAULT 0,
    month_year DATE, -- '2026-04'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, month_year)
);
```

---

## 4. API SPEC (OpenAPI)

```yaml
openapi: 3.0.0
info:
  title: CloudOps AI API
  version: 1.0.0
  description: Alert diagnosis platform

servers:
  - url: https://api.cloudopsai.com/api/v1

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

  schemas:
    Alert:
      type: object
      properties:
        id: { type: string, format: uuid }
        rule_name: { type: string }
        category: { type: string, enum: [cpu_pressure, availability, cost_anomaly, unknown] }
        severity: { type: string }
        created_at: { type: string, format: date-time }
        diagnosis: { $ref: '#/components/schemas/Diagnosis' }

    Diagnosis:
      type: object
      properties:
        diagnosis: { type: string }
        evidence: { type: array, items: { type: string } }
        suggested_action: { type: string }
        confidence: { type: number, minimum: 0, maximum: 1 }

paths:
  /webhooks/alert:
    post:
      description: "Receive alert from Azure Monitor"
      security:
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
      responses:
        '202':
          description: Alert accepted for processing
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Alert' }

  /alerts:
    get:
      description: "List alerts for tenant"
      security:
        - BearerAuth: []
      parameters:
        - name: date_from
          in: query
          schema: { type: string, format: date }
        - name: category
          in: query
          schema: { type: string }
        - name: severity
          in: query
          schema: { type: string }
        - name: limit
          in: query
          schema: { type: integer, default: 50 }
        - name: offset
          in: query
          schema: { type: integer, default: 0 }
      responses:
        '200':
          description: List of alerts
          content:
            application/json:
              schema:
                type: object
                properties:
                  total: { type: integer }
                  alerts: { type: array, items: { $ref: '#/components/schemas/Alert' } }

  /alerts/{id}:
    get:
      security:
        - BearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Alert' }

  /auth/signup:
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email: { type: string }
                password: { type: string }
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                type: object
                properties:
                  token: { type: string }

  /auth/login:
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email: { type: string }
                password: { type: string }
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
                properties:
                  token: { type: string }

  /integrations/slack/oauth:
    get:
      description: "Slack OAuth callback"
      parameters:
        - name: code
          in: query
          required: true
          schema: { type: string }
      responses:
        '200':
          description: Slack connected

  /api-keys:
    post:
      security:
        - BearerAuth: []
      responses:
        '201':
          description: API key generated
          content:
            application/json:
              schema:
                type: object
                properties:
                  key: { type: string }
```

---

## 5. COPY & MESSAGING (LATAM-focused)

### Landing page headline
**ES:** "Diagnostica alertas automáticamente. Reduce MTTR de horas a minutos."  
**Subheading:** "Deja de investigar alertas falsas. CloudOps AI te dice qué pasó en 3 segundos."

### Social proof
**ES:** "Usado por DevOps teams en fintechs, startups y unicornios de LATAM"

### Pricing messaging
**ES:** 
- Free: "Perfecto para probar" (1,000 alerts/mes)
- Pro: "Para teams que quieren responder rápido" ($99/mes LATAM pricing)
- Enterprise: "Soluciones customizadas para grandes operaciones"

### CTA copy
**ES:** "Comienza gratis" (not "Start free" — feels natural in Spanish)

---

## 6. DESIGN SYSTEM (Minimal)

### Colors
- **Primary:** #3B82F6 (Blue — tech, trust)
- **Success:** #10B981 (Green — resolved)
- **Warning:** #F59E0B (Amber — investigating)
- **Danger:** #EF4444 (Red — critical)
- **Neutral:** #6B7280 (Gray — text)

### Typography
- **Headings:** Inter, 600-700 weight
- **Body:** Inter, 400 weight
- **Code:** Courier, monospace

### Components (shadcn/ui)
- Buttons (primary, secondary, ghost)
- Tables (sortable, filterable)
- Badges (category, severity)
- Modals (setup wizard)
- Slide-out panels (alert detail)

---

## 7. LANDING PAGE STRUCTURE

```
Hero section
├─ Headline + subheading
├─ Screenshot of dashboard
└─ CTA: "Comienza gratis"

Problem section
├─ "El problema: Alert fatigue"
├─ "Tus DevOps gastan 2 horas/día investigando alertas"
├─ Stats: "70% reducción en MTTR"

Solution section
├─ "CloudOps AI diagnostica automáticamente"
├─ "Con IA que entiende tu infraestructura"
├─ Feature list with icons

Pricing section
├─ Free | Pro | Enterprise tiers
├─ Pricing table
└─ FAQ accordion

Social proof
├─ "Usado por teams en..." (logos de ejemplo)
├─ Quote: "Nos ahorra 1 FTE en ops" — Juan, SRE Lead

CTA footer
└─ "Comienza gratis hoy"
```

---

## 8. NEXT STEPS (Week 4+)

1. **Figma mockups** — Use this wireframe spec to build polished designs
2. **Copy writing** — Refine Spanish messaging (hire copywriter si es necesario)
3. **Frontend scaffolding** — React + Vite setup matches these wireframes
4. **Backend foundation** — PostgreSQL schema matches database spec above

---

**Status: SPEC COMPLETE**

**Next: Week 4 (Backend) can start immediately with this spec.**

