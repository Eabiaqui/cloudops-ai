# CloudOps AI — Product Roadmap

**Objetivo:** Ir al mercado en 10 semanas con MVP vendible.

**Timeline:** 2026-04-07 → 2026-06-16 (launch)

---

## Phase 1: Validación (Semana 1-2) ⚡

### Objetivo
Validar que el problema existe y que alguien lo pagaría.

### Tareas
- [ ] **Entrevista 5 DevOps leads** (45 min cada una)
  - Script: "¿Cuánto tiempo gastan en investigar alertas? ¿Qué frustración sienten?"
  - Target: LinkedIn, Kubernetes Slack, ex-colegas
  - Meta: 3 "eso resuelve un dolor" + 2 "estaría dispuesto a probar"

- [ ] **Prueba product con 2 beta users internos**
  - Dale acceso al webhook actual + logs
  - "¿Esto te ayuda a diagnosticar más rápido?"

- [ ] **Define buyer persona de forma clara**
  - Nombre, empresa, presupuesto, proceso de compra
  - Ejemplo: "Juan, SRE Lead en fintech, 5 engineers, decide compras <$1k/mes"

### Deliverables
- [ ] Documento: "Customer Discovery Notes" (5 entrevistas)
- [ ] Documento: "Buyer Persona" (perfil detallado)
- [ ] Decisión: ¿Seguimos? (si feedback es positivo)

### Duración
**2 semanas** (puedes hacer entrevistas en paralelo a código)

---

## Phase 2: MVP Design & Product Spec (Semana 3) 🎨

### Objetivo
Definir exactamente qué vamos a construir para ser vendible.

### Tareas

#### 2a. Define core user flows
- [ ] **Flow 1: Setup inicial** (5 min)
  - Usuario nuevo → conecta Azure/AWS → webhook automático
  - UI: Wizard de 3 pasos con copiar-pegar

- [ ] **Flow 2: Dashboard - Ver alertas** (daily driver)
  - Tabla de últimas 100 alertas
  - Columnas: timestamp | alert_rule | category | diagnosis | status
  - Filtros: date range + category + severity

- [ ] **Flow 3: Ver diagnosis**
  - Clic en alerta → slide-out panel
  - Muestra: diagnosis | evidence | suggested_action | confidence
  - Botones: "Approve remediation" | "Ignore" | "Escalate"

- [ ] **Flow 4: Slack notification**
  - Alerta crítica → notificación Slack
  - Botón: "View in CloudOps" (link a dashboard)
  - Post: diagnosis + 1 línea de acción

#### 2b. Define data model (PostgreSQL schema)

```sql
-- Multi-tenant tables
tenants (id, name, api_key, plan, created_at)
users (id, tenant_id, email, role)

-- Core
alerts (id, tenant_id, alert_id_external, rule_name, category, confidence, severity, payload_raw)
diagnoses (id, alert_id, diagnosis, evidence[], suggested_action, confidence, created_at)
audit_logs (id, tenant_id, action, details, created_at)

-- Integrations
slack_configs (id, tenant_id, webhook_url, channel_id)
azure_configs (id, tenant_id, subscription_id, encrypted_secret)

-- Remediation (Fase 2, opcional para MVP)
remediations (id, alert_id, action, status, approved_by, executed_at)
```

#### 2c. Define API endpoints (MVP only)

```
POST   /api/v1/webhooks/alert         # Azure → alert ingestion
GET    /api/v1/alerts                 # Dashboard query
GET    /api/v1/alerts/{id}            # Single alert detail
POST   /api/v1/alerts/{id}/silence    # Silence this alert type
GET    /api/v1/setup/wizard           # Setup flow

# Auth
POST   /api/v1/auth/keys              # Generate API key
```

#### 2d. Design dashboard wireframes (Figma)
- [ ] Homepage: Setup wizard OR dashboard (based on status)
- [ ] Dashboard: Table view de alertas
- [ ] Alert detail: Diagnosis sidebar
- [ ] Settings: Slack config + API keys

### Deliverables
- [ ] Product spec doc (10-15 página, detallado)
- [ ] Figma wireframes (4-5 screens)
- [ ] Database schema diagram (ERD)
- [ ] API spec (OpenAPI/Swagger)

### Duración
**1 semana** (puede solaparse con validación)

---

## Phase 3: MVP Code (Semana 4-8) 💻

### Semana 4: Backend foundation
- [ ] PostgreSQL setup (local + RDS preview)
- [ ] User auth + JWT
- [ ] Multi-tenant middleware
- [ ] Alert model + CRUD endpoints
- [ ] Integrate existing classifier (lo que ya tienes)

### Semana 5: Frontend scaffolding
- [ ] React project setup (Vite + shadcn/ui)
- [ ] Auth flow (login/register)
- [ ] Dashboard layout (sidebar + alerts table)
- [ ] Integrate /alerts API

### Semana 6: Dashboard features
- [ ] Alerts table con sorting + filtering
- [ ] Alert detail panel
- [ ] Real-time updates (WebSocket o polling)
- [ ] Diagnosis rendering

### Semana 7: Setup wizard + integrations
- [ ] Azure setup flow (copy API key → webhook auto-config)
- [ ] Slack integration (OAuth + webhook config)
- [ ] API key generation
- [ ] Audit logs

### Semana 8: Polish + testing
- [ ] E2E testing (alert → dashboard → Slack)
- [ ] Error handling + edge cases
- [ ] Performance (load test)
- [ ] Docs + README
- [ ] Deployment (Docker)

### Deliverables
- [ ] GitHub repo (public, con MIT license para credibility)
- [ ] Deployed MVP (staging en Azure/Vercel)
- [ ] Documentation (setup guide + API docs)
- [ ] 1 working example (Azure test account + real alerts)

### Duración
**5 semanas** (aggressive but doable)

---

## Phase 4: Beta Launch + Validation (Semana 9-10) 🚀

### Semana 9: Go-to-Beta
- [ ] Public landing page (simple: problem → solution → sign up)
- [ ] Free tier (1,000 alerts/month)
- [ ] Beta invite email to discovery contacts
- [ ] Documentation (how to connect Azure)
- [ ] Post en Dev.to, Product Hunt, Kubernetes Slack

### Semana 10: Gather feedback
- [ ] User interviews (2-3 beta users)
  - Setup friction?
  - Diagnosis útil?
  - ¿Pagarían?
- [ ] Usage metrics (Amplitude o similar)
  - Alerts processed/day
  - Dashboard active users
  - Slack click-through rate
- [ ] Bug fixes based on feedback

### Deliverables
- [ ] Landing page + signup
- [ ] Beta in production
- [ ] Feedback doc + metrics
- [ ] Decision: ¿Pronto a launch en precio Pro?

### Duración
**2 semanas**

---

## Pricing & Launch Plan

### Semana 10-11: Set up payments
- [ ] Stripe integration (SaaS billing)
- [ ] Pricing page
- [ ] Billing dashboard
- [ ] Invoice automation

### Día 77 (semana 11): LAUNCH

**Precios:**
- Free: 1,000 alerts/month
- Pro: $299/month (10,000 alerts)
- Enterprise: custom

**Where to launch:**
1. Product Hunt (días 1-3)
2. DevOps communities (Kubernetes Slack, r/devops)
3. Direct outreach to beta users + discovery contacts
4. Dev.to article (case study: "How we reduced MTTR 70%")

---

## Success Metrics (Goal por semana 10)

| Métrica | Target | Viabilidad |
|---|---|---|
| Beta signups | 50+ | 70% (si design es bueno) |
| Alerts processed | 100k+ total | 80% (si usuarios lo usan) |
| Slack integration % | 30%+ adopted | 60% (debe ser friction-free) |
| Setup time | <5 min | 90% (critical path) |
| "Would you pay" | 3/5 beta users | 50% (dependent on feedback) |

---

## Decisiones clave AHORA

### 1. Validación: ¿Hablamos con DevOps leads esta semana?

**Action:** Envía message a 5 contactos hoy.

Template:
```
"Hola X, soy Eduardo. Estoy construyendo una herramienta que 
diagnostica automáticamente alertas de infraestructura con IA.

¿Te gustaría una demo en 30 min? Busco feedback de gente como 
tú que vive con alert fatigue."
```

### 2. Hosting: ¿Dónde vas a deployar?

**Recomendación:**
- Frontend: Vercel (free + auto-deploy from GitHub)
- Backend: Railway o Render (cheap PostgreSQL + FastAPI)
- Database: Railway PostgreSQL ($7/month) o AWS free tier
- Total costo: ~$30-50/month para MVP

### 3. Branding: ¿Mantienes el nombre "CloudOps AI"?

**Alternativas considerar:**
- CloudOps AI ← simple, clara
- Sentinel ← fancy pero genérico
- NocGPT ← descriptivo pero malo nombre
- Pathfinder ← good name but taken

**Recommendation: CloudOps AI** (ya has invertido en el dominio)

### 4. Legal: ¿Necesitas LLC/SRL ahora?

**Answer:** No para MVP. En beta (semana 9) sí.

---

## Weekly Standup Template

**Cada lunes documentar:**
```
## Week X Status

### Completed
- [ ] Task 1
- [ ] Task 2

### Blocked
- [ ] Anything slowing you down?

### Next week
- [ ] Plan de 3 tareas max

### Metrics (if applicable)
- Alerts processed: X
- Beta users: Y
- Feedback score: Z
```

---

## Roles & Responsibilities

**You (Eduardo):**
- Product owner (design decisions)
- Backend lead (FastAPI + PostgreSQL)
- Sales/founder (customer discovery + launch)

**Hiring needed (Fase 2 post-launch):**
- Frontend engineer (React specialist)
- DevRel/Growth (content + community)
- Support (customer onboarding)

---

## Commit

**Are you ready to:**
- [ ] Do 5 customer discovery interviews this week?
- [ ] Pause Azure SDK work for 10 weeks?
- [ ] Work MVP-mode (fast, good-enough, not perfect)?
- [ ] Launch publicly with beta feedback loop?

**If YES to all:** Start Phase 1 this week.  
**If NO to any:** Let's re-scope.

---

## Next step

1. **Today/Tomorrow:** Send 5 discovery messages
2. **This week:** Complete interviews (20 hours)
3. **Next week:** Start product spec + design

---

**Status:** Ready to execute. Give go-ahead when ready.
