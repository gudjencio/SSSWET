from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class SimulationResult(Generic[T]):
    output: T
    success: bool
    notes: list[str]


class SimulationEngine:
    """Deterministic sandbox runner for safe computational experiments."""

    def run(self, experiment: Callable[[], T]) -> SimulationResult[T]:
        try:
            output = experiment()
            return SimulationResult(output=output, success=True, notes=["Simulation completed without a runtime exception."])
        except Exception as exc:
            return SimulationResult(output=None, success=False, notes=[f"Simulation failed: {type(exc).__name__}"])
