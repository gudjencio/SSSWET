"""Explicit agent capability matrix for safer task routing."""
from __future__ import annotations

class AgentCapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, set[str]] = {}

    def register(self, agent_id: str, capabilities: list[str]) -> None:
        if not agent_id.strip():
            raise ValueError("agent_id is required")
        cleaned = {str(item).strip().casefold() for item in capabilities if str(item).strip()}
        if not cleaned:
            raise ValueError("at least one capability is required")
        self._capabilities[agent_id] = cleaned

    def eligible(self, capability: str) -> list[str]:
        requested = capability.strip().casefold()
        if not requested:
            raise ValueError("capability is required")
        return sorted(agent for agent, values in self._capabilities.items() if requested in values)

    def coverage(self, required: list[str]) -> dict:
        missing = [item for item in required if not self.eligible(item)]
        return {"required": required, "missing": missing, "complete": not missing, "execution_not_started": True}
