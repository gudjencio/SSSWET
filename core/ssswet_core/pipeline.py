from dataclasses import dataclass

from .decomposer import SubtaskSpec, TaskDecomposer
from .engine import SSSWETEngine
from .groups import GroupManager
from .providers import DeterministicDemoProvider, ProviderResult, ResearchProvider


@dataclass(frozen=True)
class PipelineStep:
    subtask: SubtaskSpec
    provider: str
    result: ProviderResult


class ResearchPipeline:
    """Coordinates decomposition, specialist work and later verification."""

    def __init__(self, engine: SSSWETEngine | None = None, provider: ResearchProvider | None = None):
        self.engine = engine or SSSWETEngine()
        self.decomposer = TaskDecomposer()
        self.groups = GroupManager()
        self.provider = provider or DeterministicDemoProvider()

    def start(self, objective: str, domain: str = "general") -> tuple[str, list[PipelineStep]]:
        task = self.engine.submit(objective, domain)
        subtasks = self.decomposer.decompose(objective, domain)
        assignments = self.engine.tick()
        assigned_ids = {task_id for _, task_id in assignments}
        if task.id not in assigned_ids:
            return task.id, []

        # The initial implementation records work products; future providers
        # can perform real research without changing the orchestration contract.
        results: list[PipelineStep] = []
        for subtask in subtasks:
            result = self.provider.investigate(subtask.objective, "initial")
            results.append(PipelineStep(subtask, self.provider.name, result))
        return task.id, results
