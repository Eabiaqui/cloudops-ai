# CloudOps AI

Autonomous NOC alert classifier powered by LangGraph + Claude + Azure.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY and Azure credentials
```

## Run

```bash
python -m cloudops_ai
```

## Test

```bash
# Unit tests
pytest

# Send sample alerts to running server
python scripts/test_webhook.py
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /alert | Receive Azure Monitor webhook |
| GET | /alerts/recent | Last 100 classified alerts |
| GET | /docs | Swagger UI |

## Systemd (Oracle server)

```bash
sudo cp cloudops-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cloudops-ai
sudo systemctl start cloudops-ai
```
