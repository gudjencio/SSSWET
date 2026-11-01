from dataclasses import dataclass

from .decomposer import SubtaskSpec, TaskDecomposer
from .engine import SSSWETEngine
from .groups import GroupManager
from .models import Agent, ResearchEvent, TaskStatus
from .providers import DeterministicDemoProvider, ProviderResult, ResearchProvider


@dataclass(frozen=True)
class PipelineStep:
    subtask: SubtaskSpec
    provider: str
    result: ProviderResult
    agent_id: str


class ResearchPipeline:
    """Run each decomposed work unit with a role-matched agent."""

    def __init__(self, engine: SSSWETEngine | None = None, provider: ResearchProvider | None = None):
        self.engine = engine or SSSWETEngine()
        self.decomposer = TaskDecomposer()
        self.groups = GroupManager()
        self.provider = provider or DeterministicDemoProvider()

    def start(self, objective: str, domain: str = "general") -> tuple[str, list[PipelineStep]]:
        task = self.engine.submit(objective, domain)
        subtasks = self.decomposer.decompose(objective, domain)
        agents: list[Agent] = []

        try:
            agents = self.engine.orchestrator.assign_team(
                task,
                [subtask.role for subtask in subtasks],
            )
            self.groups.create(task.id, agents, "specialist research and independent verification")
            self.engine.orchestrator.events.append(ResearchEvent(
                "group_created",
                "Research group created with role-matched agents.",
                task.id,
            ))

            results: list[PipelineStep] = []
            for subtask, agent in zip(subtasks, agents, strict=True):
                result = self.provider.investigate(subtask.objective, "initial")
                results.append(PipelineStep(subtask, self.provider.name, result, agent.id))
                self.engine.orchestrator.events.append(ResearchEvent(
                    "research_pass",
                    f"{agent.role} completed a research pass; evidence remains subject to verification.",
                    task.id,
                    agent.id,
                ))

            # Demo/provider outputs are not automatically promoted to findings.
            self.engine.orchestrator.complete(task, agents[0].id, accepted=True)
            self.engine.orchestrator.release_team(agents[1:], completed=True)
            return task.id, results
        except Exception:
            if agents:
                self.engine.orchestrator.release_team(agents)
            if task.status != TaskStatus.QUEUED:
                task.status = TaskStatus.BLOCKED
                self.engine.orchestrator.tasks.append(task)
                self.engine.orchestrator.events.append(ResearchEvent(
                    "pipeline_blocked",
                    "Work was preserved in the queue after a provider or allocation failure.",
                    task.id,
                ))
            raise
