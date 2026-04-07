"""Configuration for Qhunu Agent Pool."""

import os
from typing import Literal

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# LLMs
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Paths
POOL_HOME = os.path.expanduser("~/qhunu-pool")
LOGS_DIR = os.path.join(POOL_HOME, "logs")
REPORTS_DIR = os.path.join(POOL_HOME, "reports")

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Agent models
AGENT_MODELS: dict[str, tuple[Literal["ollama", "claude"], str]] = {
    "forge": ("ollama", "mistral-7b"),  # Developer + QA
    "viper": ("claude", "claude-sonnet-4-20250514"),  # Security Sentinel
    "atlas": ("ollama", "neural-chat-14b"),  # DevOps + SRE Healer
    "oracle": ("claude", "claude-haiku-4-5-20251001"),  # Benchmarker + FinOps
    "lumen": ("claude", "claude-haiku-4-5-20251001"),  # UX Sentinel
    "scribe": ("ollama", "mistral-7b"),  # Tech Writer + Archivista
}

# Agent scheduling
AGENT_SCHEDULES = {
    "forge": {"type": "interval", "minutes": 30},  # 30min cycle
    "viper": {"type": "interval", "minutes": 60},  # 1h scan cycle
    "atlas": {"type": "interval", "minutes": 5},  # 5min monitoring
    "oracle": {"type": "cron", "cron": "0 0 * * *"},  # 00:00 UTC daily
    "lumen": {"type": "cron", "cron": "0 6 * * 5"},  # Friday 06:00 UTC
    "scribe": {"type": "cron", "cron": "0 2 * * *"},  # 02:00 UTC nightly
}

# Concurrency rules
OLLAMA_MAX_CONCURRENT = 1  # Never 2 Ollama agents simultaneously
CLAUDE_RATE_LIMIT = 100  # RPM for Claude endpoints
