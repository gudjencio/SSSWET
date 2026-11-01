from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ProviderResult:
    summary: str
    evidence: tuple[str, ...] = ()
    uncertainty: float = 1.0


class ResearchProvider(Protocol):
    name: str

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        ...


class DeterministicDemoProvider:
    """Safe local provider used until real research/model providers are configured."""

    name = "deterministic-demo"

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        return ProviderResult(
            summary=f"Demo research pass for: {objective}",
            evidence=(f"Strategy recorded: {strategy}",),
            uncertainty=1.0,
        )
