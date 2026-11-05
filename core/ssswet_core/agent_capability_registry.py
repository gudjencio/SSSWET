"""Explainable capability and capacity matching for research-agent routing."""
from __future__ import annotations


class AgentCapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, set[str]] = {}
        self._profiles: dict[str, dict] = {}

    @staticmethod
    def _clean_capabilities(values: list[str], field: str) -> set[str]:
        if not isinstance(values, list):
            raise ValueError(f"{field} must be a list")
        cleaned = set()
        for item in values:
            if not isinstance(item, str) or not item.strip():
                raise ValueError(f"{field} must contain non-empty strings")
            cleaned.add(item.strip().casefold())
        return cleaned

    def register(
        self,
        agent_id: str,
        capabilities: list[str],
        *,
        status: str = "available",
        active_tasks: int = 0,
        max_concurrent_tasks: int = 1,
        preferred_domains: list[str] | None = None,
    ) -> None:
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id is required")
        if status not in {"available", "busy", "offline", "paused"}:
            raise ValueError("unsupported agent status")
        if isinstance(active_tasks, bool) or not isinstance(active_tasks, int) or active_tasks < 0:
            raise ValueError("active_tasks must be a non-negative integer")
        if isinstance(max_concurrent_tasks, bool) or not isinstance(max_concurrent_tasks, int) or max_concurrent_tasks < 1:
            raise ValueError("max_concurrent_tasks must be a positive integer")
        cleaned = self._clean_capabilities(capabilities, "capabilities")
        if not cleaned:
            raise ValueError("at least one capability is required")
        preferred = self._clean_capabilities(preferred_domains or [], "preferred_domains")
        identifier = agent_id.strip()
        self._capabilities[identifier] = cleaned
        self._profiles[identifier] = {
            "status": status,
            "active_tasks": active_tasks,
            "max_concurrent_tasks": max_concurrent_tasks,
            "preferred_domains": preferred,
        }

    def eligible(self, capability: str) -> list[str]:
        requested = capability.strip().casefold()
        if not requested:
            raise ValueError("capability is required")
        return sorted(agent for agent, values in self._capabilities.items() if requested in values)

    def coverage(self, required: list[str]) -> dict:
        missing = [item for item in required if not self.eligible(item)]
        return {"required": required, "missing": missing, "complete": not missing, "execution_not_started": True}

    def rank_for_task(
        self,
        required: list[str],
        *,
        preferred: list[str] | None = None,
        excluded_agents: set[str] | list[str] | tuple[str, ...] = (),
        limit: int = 20,
    ) -> dict:
        """Rank agents by full capability coverage, declared preferences and available capacity."""
        required_set = self._clean_capabilities(required, "required")
        if not required_set:
            raise ValueError("at least one required capability is needed")
        preferred_set = self._clean_capabilities(preferred or [], "preferred")
        excluded = {str(item).strip() for item in excluded_agents if str(item).strip()}
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")

        candidates = []
        exclusions = []
        partial_matches = []
        for agent_id, capabilities in self._capabilities.items():
            profile = self._profiles[agent_id]
            missing = sorted(required_set - capabilities)
            blocked = None
            if agent_id in excluded:
                blocked = "explicitly_excluded"
            elif profile["status"] != "available":
                blocked = "agent_not_available"
            elif profile["active_tasks"] >= profile["max_concurrent_tasks"]:
                blocked = "capacity_exhausted"
            if blocked:
                exclusions.append({"agent_id": agent_id, "reason": blocked})
                continue
            matched_preferred = sorted((preferred_set | profile["preferred_domains"]) & capabilities)
            utilization = profile["active_tasks"] / profile["max_concurrent_tasks"]
            score = round(100.0 - (20.0 * utilization) + (5.0 * len(matched_preferred)), 3)
            item = {
                "agent_id": agent_id,
                "score": score,
                "required_capabilities": sorted(required_set),
                "matched_capabilities": sorted(required_set & capabilities),
                "missing_capabilities": missing,
                "preferred_matches": matched_preferred,
                "active_tasks": profile["active_tasks"],
                "max_concurrent_tasks": profile["max_concurrent_tasks"],
                "utilization": utilization,
                "eligible": not missing,
            }
            if missing:
                partial_matches.append(item)
            else:
                candidates.append(item)

        candidates.sort(key=lambda item: (-item["score"], item["active_tasks"], item["agent_id"]))
        partial_matches.sort(key=lambda item: (-len(item["matched_capabilities"]), -item["score"], item["agent_id"]))
        return {
            "candidates": candidates[:limit],
            "partial_matches": partial_matches[:limit],
            "excluded_agents": sorted(exclusions, key=lambda item: item["agent_id"]),
            "required_capabilities": sorted(required_set),
            "eligible_count": len(candidates),
            "partial_match_count": len(partial_matches),
            "assignment_executed": False,
            "autonomous_execution_authorized": False,
        }
