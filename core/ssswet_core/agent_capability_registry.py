"""Explicit, least-privilege agent capability matching for research task routing."""
from __future__ import annotations

MAX_AGENTS = 1000
MAX_HISTORY = 1000


class AgentCapabilityRegistry:
    """Match declared capabilities; recommendations never start or delegate work."""
    def __init__(self) -> None:
        self._capabilities: dict[str, set[str]] = {}
        self._versions: dict[str, int] = {}
        self._history: list[dict] = []

    @staticmethod
    def _identifier(value: str, field: str) -> str:
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > 120:
            raise ValueError(f"{field} must contain 1 to 120 characters")
        return value.strip()

    @staticmethod
    def _capability_list(values: list[str], field: str) -> set[str]:
        if not isinstance(values, list) or len(values) > 100:
            raise ValueError(f"{field} must be a list of at most 100 capabilities")
        cleaned = set()
        for value in values:
            if not isinstance(value, str) or not value.strip() or len(value.strip()) > 100:
                raise ValueError(f"{field} entries must contain 1 to 100 characters")
            cleaned.add(value.strip().casefold())
        return cleaned

    def register(self, agent_id: str, capabilities: list[str]) -> dict:
        agent_id = self._identifier(agent_id, "agent_id")
        cleaned = self._capability_list(capabilities, "capabilities")
        if not cleaned:
            raise ValueError("at least one capability is required")
        if agent_id not in self._capabilities and len(self._capabilities) >= MAX_AGENTS:
            raise ValueError(f"registry is limited to {MAX_AGENTS} agents")
        version = self._versions.get(agent_id, 0) + 1
        self._versions[agent_id] = version
        self._capabilities[agent_id] = cleaned
        record = {"agent_id": agent_id, "version": version, "capabilities": sorted(cleaned)}
        self._history.append(record.copy())
        if len(self._history) > MAX_HISTORY:
            del self._history[:len(self._history) - MAX_HISTORY]
        return record

    def eligible(self, capability: str) -> list[str]:
        requested = self._identifier(capability, "capability").casefold()
        return sorted(agent for agent, values in self._capabilities.items() if requested in values)

    def coverage(self, required: list[str]) -> dict:
        requested = sorted(self._capability_list(required, "required"))
        missing = [item for item in requested if not self.eligible(item)]
        return {"required": requested, "missing": missing, "complete": not missing, "execution_not_started": True}

    def recommend(self, required: list[str], *, forbidden: list[str] | None = None, limit: int = 10) -> dict:
        requested = self._capability_list(required, "required")
        excluded = self._capability_list(forbidden or [], "forbidden")
        if not requested:
            raise ValueError("at least one required capability is needed")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        matches, excluded_agents = [], []
        for agent_id, capabilities in self._capabilities.items():
            blocked = sorted(capabilities & excluded)
            if blocked:
                excluded_agents.append({"agent_id": agent_id, "forbidden_capabilities": blocked})
                continue
            matched = sorted(capabilities & requested)
            if not matched:
                continue
            missing = sorted(requested - capabilities)
            matches.append({
                "agent_id": agent_id, "matched_capabilities": matched,
                "missing_capabilities": missing, "coverage": len(matched) / len(requested),
                "complete_match": not missing, "registry_version": self._versions[agent_id],
            })
        matches.sort(key=lambda item: (not item["complete_match"], -len(item["matched_capabilities"]), item["agent_id"]))
        return {
            "required_capabilities": sorted(requested), "matches": matches[:limit],
            "excluded_agents": sorted(excluded_agents, key=lambda item: item["agent_id"]),
            "candidate_count": len(matches), "complete_match_count": sum(item["complete_match"] for item in matches),
            "automatic_assignment": False, "execution_not_started": True,
        }

    def history(self, *, limit: int = 200) -> list[dict]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_HISTORY:
            raise ValueError(f"limit must be between 1 and {MAX_HISTORY}")
        return [item.copy() for item in self._history[-limit:]]
