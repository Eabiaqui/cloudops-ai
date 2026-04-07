"""
Local Model Configuration - Zero API Costs

All agents use Ollama (local) for cost efficiency.
Claude API fallback disabled.
"""

OLLAMA_BASE_URL = "http://127.0.0.1:11434"

AGENT_MODELS_LOCAL = {
    "qhunu": {
        "type": "ollama",
        "model": "mistral",
        "params": {"temperature": 0.7, "top_p": 0.9}
    },
    "forge": {
        "type": "ollama",
        "model": "mistral",
        "params": {"temperature": 0.5}  # Lower temp for code
    },
    "viper": {
        "type": "ollama",
        "model": "neural-chat",
        "params": {"temperature": 0.3}  # Very low for security
    },
    "atlas": {
        "type": "ollama",
        "model": "neural-chat",
        "params": {"temperature": 0.5}
    },
    "oracle": {
        "type": "ollama",
        "model": "mistral",
        "params": {"temperature": 0.4}  # Low for analysis
    },
    "lumen": {
        "type": "ollama",
        "model": "mistral",
        "params": {"temperature": 0.6}
    },
    "scribe": {
        "type": "ollama",
        "model": "mistral",
        "params": {"temperature": 0.5}
    },
}

# Cost breakdown
COST_TRACKER = {
    "claude_api_cost": 0.0,  # Disabled, using local models
    "ollama_cost": 0.0,      # Free (local)
    "infrastructure": 46.0,   # Monthly fixed cost
    "total_monthly": 46.0,    # Guaranteed maximum
}

# No rate limits with local models
RATE_LIMITS = {
    "requests_per_minute": "unlimited",
    "concurrent_calls": "unlimited",
    "daily_cost_limit": "0.00",
}

print("Local model configuration loaded")
print("All agents using Ollama (free, local, unlimited)")
print("Zero API costs. Full autonomy.")
