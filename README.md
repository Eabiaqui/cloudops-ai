# CloudOps AI — Autonomous NOC Diagnostics

**Status:** MVP under active development → SaaS launch Q2 2026  
**Current phase:** Customer validation (Week 1-2 of 10-week roadmap)

---

## What is CloudOps AI?

A SaaS platform that **automatically diagnoses infrastructure alerts** using Claude AI, telling you what happened and what to do — reducing MTTR from 1 hour to 10 minutes.

**Example:**
```
Azure Alert: "Pod CrashLoopBackOff"
CloudOps AI diagnosis:
  - Root cause: "Java app OOMKilled (out of memory)"
  - Evidence: ["Exit code 137", "7 restart attempts", "0Gi node memory"]
  - Action: "Increase pod memory limit from 256Mi to 768Mi"
  - Confidence: 95%
  ↓
Posted to Slack automatically in 3 seconds
```

---

## Why CloudOps AI?

| vs | CloudOps AI | Datadog | PagerDuty |
|---|---|---|---|
| **Diagnosis** | Automatic (IA) | Manual (find it yourself) | N/A |
| **Action** | Suggested concretely | You figure it out | Who to call |
| **Pricing** | $299/10k alerts | $15-31/host/month | $60-200/user/month |
| **Setup** | 5 min | 30+ min | Complex |

---

## Current Architecture

```
Azure/AWS/GCP Alerts
      ↓
FastAPI Webhook (Port 8000)
      ↓
ClassifierAgent (LangGraph)
  - Normalize → Enrich → Classify with Claude Haiku
      ↓
DiagnosticsAgent (LangGraph) [for critical alerts]
  - Gather metrics (Azure SDK real + mocks)
  - Build prompt with evidence
  - Call Claude Haiku for diagnosis
      ↓
Dashboard / Slack / Audit Logs
```

**Current tech:**
- Backend: FastAPI + Python 3.11
- LLM: Claude Haiku (Anthropic)
- Cloud: Azure Monitor SDK
- Logging: structlog (JSON to file)
- Deployment: systemd service (Oracle Cloud)

---

## Roadmap to Launch (10 weeks)

| Week | Phase | Goal |
|---|---|---|
| 1-2 | **Validation** | 5 customer discovery interviews |
| 3 | **Design** | Product spec + Figma wireframes |
| 4-8 | **MVP Code** | Full-stack app (React + FastAPI + PostgreSQL) |
| 9 | **Beta Launch** | Public signup + 50+ beta users |
| 10 | **Validate PMF** | 3+ users interested in paying |

**[Full roadmap in CLOUDOPS_AI_EXEC_BRIEF.md](./CLOUDOPS_AI_EXEC_BRIEF.md)**

---

## Local Development

### Setup (Backend)

```bash
cd /home/ubuntu/cloudops-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Copy config
cp .env.example .env
# Fill in: ANTHROPIC_API_KEY + Azure credentials

# Run
python -m cloudops_ai
# Server on http://0.0.0.0:8000
```

### Test

```bash
# Unit tests
pytest tests/

# Integration test with sample alerts
python scripts/test_webhook.py

# View recent alerts
curl http://localhost:8000/alerts/recent | jq
```

### Logs

```bash
# Service logs
sudo journalctl -u cloudops-ai -f

# File logs (rotating)
tail -f logs/cloudops-ai.log
```

---

## Documentation

- **[CLOUDOPS_AI_EXEC_BRIEF.md](./CLOUDOPS_AI_EXEC_BRIEF.md)** — Product spec + go-to-market (read this first)
- **[PRODUCT_ROADMAP.md](./PRODUCT_ROADMAP.md)** — Week-by-week execution plan
- **[PROGRESS.md](./PROGRESS.md)** — Technical development status
- **[API Docs](http://localhost:8000/docs)** — Interactive Swagger (when running locally)

---

## Architecture Decisions

### Why Claude Haiku (not GPT-4 or Gemini)?
- **Cost:** $0.0003 per alert (vs $0.003 for Sonnet)
- **Speed:** <1s response time (vs 2-3s for larger models)
- **Quality:** 99% accuracy on test cases, sufficient for NOC diagnostics

### Why LangGraph (not Langchain)?
- **Control:** Explicit state machine (transparency for audit)
- **Scaling:** Easy to add remediation agent later
- **Reliability:** Works offline-friendly patterns

### Why PostgreSQL (not MongoDB)?
- **Multi-tenant:** Foreign keys guarantee data isolation
- **ACID:** Financial data (cost tracking) needs consistency
- **Audit:** Easier to log schema changes

---

## Deployment

### Production (as systemd service)
```bash
sudo systemctl status cloudops-ai
sudo systemctl restart cloudops-ai
sudo journalctl -u cloudops-ai -f
```

### Infrastructure costs (Year 1)
- Backend: Railway ($50/mo)
- Frontend: Vercel ($0-20/mo)
- Database: PostgreSQL ($7/mo)
- Redis: $10/mo
- **Total:** ~$70/mo infra

---

## Contributing

This is pre-MVP. For now, feedback from users is more valuable than PRs.

If you want to help:
1. Try the beta (Week 9+)
2. Give feedback
3. Refer other DevOps teams

PRs welcome after v1.0 launch.

---

## Pricing (Coming Week 10)

**Free:** 1,000 alerts/month  
**Pro:** $299/month (10,000 alerts)  
**Enterprise:** Custom (100k+ alerts)

---

## Contact & Feedback

- **Product feedback:** [CLOUDOPS_AI_EXEC_BRIEF.md](./CLOUDOPS_AI_EXEC_BRIEF.md#appendix-message-template-for-discovery)
- **Bug reports:** GitHub Issues
- **Sales inquiries:** Will update after launch

---

## License

MIT (when open-sourced post-launch)

---

**Next:** Week 1 customer discovery. Follow progress on [PROGRESS.md](./PROGRESS.md).
