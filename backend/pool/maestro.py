"""Maestro Agent - Orchestrates the 7-agent Qhunu Pool with smart scheduling."""

import asyncio
import json
import logging
import sys
from datetime import datetime, time
from typing import TypedDict
from croniter import croniter

import redis
from langgraph.graph import StateGraph, START, END

sys.path.insert(0, '/home/ubuntu/qhunu-pool')
from config import (
    REDIS_HOST, REDIS_PORT, LOGS_DIR,
    AGENT_SCHEDULES, OLLAMA_MAX_CONCURRENT
)
from utils.json_safe import safe_dumps, cleanup_json_response

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"{LOGS_DIR}/maestro.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("Maestro")

# Redis connection
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


class PoolState(TypedDict):
    """State for the agent pool."""
    cycle: int
    timestamp: str
    agents_status: dict
    active_ollama: int
    tasks_assigned: int
    results: dict


def initialize_state() -> PoolState:
    """Initialize pool state."""
    return {
        "cycle": 0,
        "timestamp": datetime.utcnow().isoformat(),
        "agents_status": {},
        "active_ollama": 0,
        "tasks_assigned": 0,
        "results": {},
    }


def check_agent_health(state: PoolState) -> PoolState:
    """Check all 7 agents are alive in Redis."""
    agents = ["qhunu", "forge", "viper", "atlas", "oracle", "lumen", "scribe"]
    status = {}
    
    for agent in agents:
        heartbeat = redis_client.get(f"qhunu:agent:{agent}:heartbeat")
        # Check if heartbeat is recent (< 5 min)
        status[agent] = "alive" if heartbeat else "offline"
    
    state["agents_status"] = status
    alive_count = sum(1 for s in status.values() if s == "alive")
    logger.info(f"🫀 Agent health: {alive_count}/7 alive | {status}")
    
    return state


def get_ollama_usage() -> int:
    """Count active Ollama agents in execution."""
    active = redis_client.get("qhunu:ollama:active_count")
    return int(active) if active else 0


def is_schedule_due(agent: str, last_run: str = None) -> bool:
    """Check if agent schedule is due."""
    schedule = AGENT_SCHEDULES.get(agent)
    if not schedule:
        return False
    
    if schedule["type"] == "interval":
        minutes = schedule.get("minutes", 30)
        if last_run:
            try:
                last = datetime.fromisoformat(last_run)
                elapsed = (datetime.utcnow() - last).total_seconds() / 60
                return elapsed >= minutes
            except:
                return True
        return True
    
    elif schedule["type"] == "cron":
        cron = schedule.get("cron")
        if not cron:
            return False
        
        try:
            cron_iter = croniter(cron, datetime.utcnow())
            next_run = cron_iter.get_next(datetime)
            now = datetime.utcnow()
            # Due if we're within 1 minute of next scheduled time
            return (next_run - now).total_seconds() <= 60
        except:
            return False
    
    return False


def assign_tasks(state: PoolState) -> PoolState:
    """Assign tasks based on schedule + concurrency rules."""
    state["cycle"] += 1
    state["timestamp"] = datetime.utcnow().isoformat()
    
    agents = ["forge", "viper", "atlas", "oracle", "lumen", "scribe"]
    tasks_assigned = 0
    ollama_usage = get_ollama_usage()
    
    for agent in agents:
        # Check if schedule is due
        last_run = redis_client.get(f"qhunu:agent:{agent}:last_run")
        
        if not is_schedule_due(agent, last_run):
            continue
        
        # Concurrency check: Don't queue if max Ollama concurrent reached
        if agent in ["forge", "atlas", "scribe"]:  # Ollama agents
            if ollama_usage >= OLLAMA_MAX_CONCURRENT:
                logger.warning(f"⏸️  {agent} skipped: Ollama concurrency limit ({ollama_usage}/{OLLAMA_MAX_CONCURRENT})")
                continue
        
        # Queue task
        task = {
            "agent": agent,
            "type": "cycle",
            "cycle": state["cycle"],
            "timestamp": state["timestamp"],
        }
        
        agent_queue = f"qhunu:queue:{agent}"
        redis_client.rpush(agent_queue, json.dumps(task))
        redis_client.set(f"qhunu:agent:{agent}:last_run", state["timestamp"])
        
        tasks_assigned += 1
        logger.info(f"📋 Queued {agent}")
    
    state["tasks_assigned"] = tasks_assigned
    state["active_ollama"] = ollama_usage
    
    logger.info(f"✅ Cycle {state['cycle']}: {tasks_assigned} tasks queued (Ollama: {ollama_usage}/{OLLAMA_MAX_CONCURRENT})")
    return state


def collect_alerts(state: PoolState) -> PoolState:
    """Collect critical alerts from agent queue."""
    alerts = []
    
    while True:
        alert_json = redis_client.lpop("qhunu:alerts")
        if not alert_json:
            break
        
        try:
            alert = json.loads(alert_json)
            alerts.append(alert)
        except:
            pass
    
    if alerts:
        # Log critical alerts
        critical = [a for a in alerts if a.get("severity") == "critical"]
        if critical:
            logger.warning(f"🚨 {len(critical)} CRITICAL alerts: {[a.get('message') for a in critical]}")
        
        state["results"]["alerts"] = alerts
    
    return state


def update_pool_metrics(state: PoolState) -> PoolState:
    """Update Redis pool metrics."""
    metrics = {
        "cycle": state["cycle"],
        "timestamp": state["timestamp"],
        "agents_status": state["agents_status"],
        "tasks_assigned_this_cycle": state["tasks_assigned"],
        "ollama_active": state["active_ollama"],
    }
    
    # Use safe_dumps to prevent JSON errors
    cleaned = cleanup_json_response(metrics)
    redis_client.set("qhunu:pool:metrics", safe_dumps(cleaned))
    return state


async def run_maestro_loop():
    """Main maestro orchestration loop."""
    logger.info("🎼 MAESTRO ORCHESTRATOR STARTED")
    logger.info(f"📋 Agent Schedules: {AGENT_SCHEDULES}")
    
    state = initialize_state()
    
    while True:
        try:
            # 1. Health check
            state = check_agent_health(state)
            
            # 2. Assign tasks based on schedule
            state = assign_tasks(state)
            
            # 3. Collect alerts
            state = collect_alerts(state)
            
            # 4. Update metrics
            state = update_pool_metrics(state)
            
            # Sleep before next cycle (30s default)
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"❌ Maestro error: {e}", exc_info=True)
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(run_maestro_loop())
