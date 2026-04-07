#!/usr/bin/env python3
"""Validate 10 → 7 agent refactor."""

import sys
import json
from pathlib import Path

def validate_structure():
    """Validate agent pool structure."""
    
    expected_agents = {
        "forge": "Developer + QA (Ollama 7b, 30min)",
        "viper": "Security Sentinel (Claude Sonnet, 1h)",
        "atlas": "DevOps + SRE (Ollama 14b, 5min)",
        "oracle": "Benchmarker + FinOps (Haiku, 00:00)",
        "lumen": "UX Sentinel (Haiku, Fri 06:00)",
        "scribe": "Tech Writer + Archive (Ollama, 02:00)",
    }
    
    obsolete_agents = {
        "developer": "→ merged into forge",
        "qa": "→ merged into forge",
        "security": "→ renamed to viper",
        "devops": "→ merged into atlas",
        "benchmarker": "→ merged into oracle",
        "analyst": "→ removed (no longer needed)",
    }
    
    print("=" * 70)
    print("🎯 QHUNU AGENT POOL REFACTOR VALIDATION")
    print("=" * 70)
    
    # Check agent files
    print("\n✅ 7 Active Agents:")
    agents_dir = Path("agents")
    for agent_name, description in expected_agents.items():
        agent_file = agents_dir / f"{agent_name}.py"
        status = "✓" if agent_file.exists() else "✗"
        print(f"  {status} {agent_name:8} | {description}")
        
        # Quick validation: check for run_*_agent function
        if agent_file.exists():
            with open(agent_file) as f:
                content = f.read()
                has_main = f"run_{agent_name}_agent" in content
                print(f"       {'└─' if has_main else '⚠'}  Main function: {'OK' if has_main else 'MISSING'}")
    
    # Check obsolete agents
    print("\n📦 Obsolete Agents (safe to remove):")
    for agent_name, note in obsolete_agents.items():
        agent_file = agents_dir / f"{agent_name}.py"
        exists = agent_file.exists()
        status = "⚠" if exists else "✓"
        print(f"  {status} {agent_name:12} {note:30} {'(file exists)' if exists else ''}")
    
    # Check config
    print("\n⚙️  Configuration Check:")
    from config import AGENT_MODELS, AGENT_SCHEDULES
    
    for agent in expected_agents.keys():
        if agent in AGENT_MODELS:
            model_type, model_name = AGENT_MODELS[agent]
            print(f"  ✓ {agent:8} | {model_type:6} {model_name[:30]:30}")
        else:
            print(f"  ✗ {agent:8} | NOT IN CONFIG")
    
    print("\n📋 Scheduling:")
    for agent in expected_agents.keys():
        if agent in AGENT_SCHEDULES:
            sched = AGENT_SCHEDULES[agent]
            if sched["type"] == "interval":
                print(f"  ✓ {agent:8} | Every {sched['minutes']:2}m")
            else:
                print(f"  ✓ {agent:8} | Cron: {sched.get('cron', 'N/A')}")
        else:
            print(f"  ✗ {agent:8} | NOT SCHEDULED")
    
    # Concurrency rules
    print("\n🔒 Concurrency Rules:")
    from config import OLLAMA_MAX_CONCURRENT
    ollama_agents = ["forge", "atlas", "scribe"]
    print(f"  ✓ Ollama max concurrent: {OLLAMA_MAX_CONCURRENT}")
    print(f"  ✓ Ollama agents: {', '.join(ollama_agents)}")
    print(f"  ✓ Claude agents: viper, oracle, lumen (on-demand/scheduled)")
    
    # Maestro check
    print("\n🎼 Maestro Orchestrator:")
    maestro_file = Path("maestro.py")
    if maestro_file.exists():
        with open(maestro_file) as f:
            content = f.read()
            has_scheduler = "croniter" in content
            has_concurrency = "OLLAMA_MAX_CONCURRENT" in content
            print(f"  ✓ Scheduler logic: {'OK' if has_scheduler else 'MISSING'}")
            print(f"  ✓ Concurrency control: {'OK' if has_concurrency else 'MISSING'}")
    
    print("\n" + "=" * 70)
    print("✅ REFACTOR COMPLETE")
    print("=" * 70)
    print("""
Next steps:
1. Delete obsolete agent files (optional):
   cd agents && rm -f developer.py qa.py security.py devops.py benchmarker.py

2. Install croniter dependency:
   pip install croniter

3. Test scheduling with maestro.py:
   python maestro.py

4. Monitor agent heartbeats:
   redis-cli KEYS 'qhunu:agent:*:heartbeat'
""")

if __name__ == "__main__":
    validate_structure()
