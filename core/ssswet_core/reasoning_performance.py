"""Performance policy for low-latency research-agent execution.

The policy reduces avoidable waiting without weakening evidence requirements:
- independent work may run concurrently;
- model drafts use bounded output budgets;
- slow optional sources must not block already-complete independent work;
- no timeout or speed optimisation is allowed to turn an unknown result into a claim.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReasoningPerformancePolicy:
    """Bounded execution settings for fast research passes."""

    max_parallel_agents: int = 10
    max_parallel_reviews: int = 6
    model_timeout_seconds: float = 30.0
    model_max_output_tokens: int = 700
    literature_timeout_seconds: float = 8.0
    literature_results_per_source: int = 4

    def __post_init__(self) -> None:
        if self.max_parallel_agents < 1:
            raise ValueError("max_parallel_agents must be at least 1")
        if self.max_parallel_reviews < 1:
            raise ValueError("max_parallel_reviews must be at least 1")
        if self.model_timeout_seconds < 5:
            raise ValueError("model_timeout_seconds must be at least 5 seconds")
        if not 128 <= self.model_max_output_tokens <= 3000:
            raise ValueError("model_max_output_tokens must be between 128 and 3000")
        if self.literature_timeout_seconds < 2:
            raise ValueError("literature_timeout_seconds must be at least 2 seconds")
        if not 1 <= self.literature_results_per_source <= 20:
            raise ValueError("literature_results_per_source must be between 1 and 20")

    def model_kwargs(self) -> dict[str, float | int]:
        """Return safe low-latency settings for a compatible model provider."""
        return {
            "timeout": self.model_timeout_seconds,
            "max_tokens": self.model_max_output_tokens,
        }

    def literature_kwargs(self) -> dict[str, float | int]:
        return {
            "timeout": self.literature_timeout_seconds,
            "max_results": self.literature_results_per_source,
        }


FAST_REASONING_POLICY = ReasoningPerformancePolicy()
