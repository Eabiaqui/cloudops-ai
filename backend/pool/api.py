"""FastAPI server for Qhunu Agent Pool dashboard."""

import json
from datetime import datetime
from typing import Optional

import redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS for React dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/pool/status")
async def pool_status():
    """Get full pool status for dashboard."""
    try:
        agents = ["developer", "qa", "security", "benchmarker", "devops"]
        agents_data = {}
        
        for agent in agents:
            heartbeat = redis_client.get(f"qhunu:agent:{agent}:heartbeat")
            cycle = redis_client.get(f"qhunu:cycle:{agent}")
            result_key = f"qhunu:result:{agent}:{cycle}" if cycle else None
            result = redis_client.get(result_key) if result_key else None
            
            agents_data[agent] = {
                "status": "alive" if heartbeat else "offline",
                "heartbeat": heartbeat or "never",
                "cycle": int(cycle) if cycle else 0,
                "current_result": json.loads(result) if result else None,
            }
        
        # Get maestro state
        pool_state = redis_client.get("qhunu:pool:state")
        maestro_state = json.loads(pool_state) if pool_state else {}
        
        # Get recent alerts
        alerts = []
        try:
            raw_alerts = redis_client.lrange("qhunu:alerts", 0, 19)
            for alert_json in raw_alerts:
                try:
                    alerts.append(json.loads(alert_json))
                except:
                    pass
        except:
            pass
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "maestro": maestro_state,
            "agents": agents_data,
            "alerts": alerts[-20:],  # Last 20
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pool/metrics")
async def pool_metrics():
    """Get cost and token metrics."""
    try:
        # Estimated costs per agent
        costs = {
            "developer": 0.001,  # Claude Opus
            "qa": 0,  # Ollama local
            "security": 0.0003,  # Claude Sonnet
            "benchmarker": 0.0001,  # Claude Haiku
            "devops": 0,  # Ollama local
        }
        
        total_cost = sum(costs.values())
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "costs_by_agent": costs,
            "total_cost_today": total_cost,
            "models": {
                "developer": "claude-opus-4-1",
                "qa": "ollama-llama2",
                "security": "claude-sonnet-4-20250514",
                "benchmarker": "claude-haiku-3-5",
                "devops": "ollama-llama2",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
