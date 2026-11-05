"""SSSWET core orchestration package."""

from .continuity_tools import (
    build_agent_handoff,
    build_memory_snapshot,
    candidate_memory_conflicts,
    compare_temporal_observations,
    group_exact_memory_duplicates,
    normalize_memory_query,
    parse_temporal_instant,
    query_temporal_window,
    search_memory_records,
    temporal_coverage_gaps,
    validate_memory_snapshot,
)
from .engine import SSSWETEngine
from .research_continuity import ResearchContinuityService
from .models import Agent, Finding, Task, VerificationState

__version__ = "0.2.0"

__all__ = [
    "SSSWETEngine", "ResearchContinuityService", "Agent", "Finding", "Task", "VerificationState",
    "build_agent_handoff", "build_memory_snapshot", "candidate_memory_conflicts",
    "compare_temporal_observations", "group_exact_memory_duplicates",
    "normalize_memory_query", "parse_temporal_instant", "query_temporal_window",
    "search_memory_records", "temporal_coverage_gaps", "validate_memory_snapshot",
    "__version__",
]
