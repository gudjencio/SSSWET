"""Deterministic capability-aware agent load ordering."""
from __future__ import annotations


def rank(agents: list[dict], capability: str) -> list[dict]:
    eligible = [agent for agent in agents if capability in set(agent.get("capabilities", [])) and agent.get("status") not in {"blocked", "retired"}]
    return sorted(eligible, key=lambda a: (float(a.get("load", 0.0)), -int(a.get("completed_tasks", 0)), str(a.get("id", ""))))
