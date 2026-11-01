from dataclasses import dataclass


@dataclass(frozen=True)
class Strategy:
    name: str
    purpose: str


STRATEGIES = (
    Strategy("direct", "Attempt the simplest valid approach."),
    Strategy("decompose", "Split the objective into smaller independently testable parts."),
    Strategy("recompute", "Recalculate the result independently using a different derivation."),
    Strategy("contradict", "Actively search for counterexamples, inconsistencies, or boundary failures."),
    Strategy("alternative_model", "Test a materially different model or assumption set."),
    Strategy("source_review", "Compare reliable external evidence and record provenance."),
)


class StrategySelector:
    def __init__(self) -> None:
        self._cursor = 0

    def next(self, previous: list[str] | None = None) -> Strategy:
        previous = previous or []
        for _ in range(len(STRATEGIES)):
            strategy = STRATEGIES[self._cursor % len(STRATEGIES)]
            self._cursor += 1
            if strategy.name not in previous or len(previous) >= len(STRATEGIES):
                return strategy
        return STRATEGIES[0]

    @staticmethod
    def materially_different(previous: str, candidate: str) -> bool:
        return previous != candidate
