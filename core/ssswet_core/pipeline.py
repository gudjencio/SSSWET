from dataclasses import dataclass

from .decomposer import SubtaskSpec, TaskDecomposer
from .engine import SSSWETEngine
from .groups import GroupManager
from .models import Agent, ResearchEvent, TaskStatus
from .persistence import SQLiteResearchStore
from .providers import DeterministicDemoProvider, ProviderResult, ResearchProvider


@dataclass(frozen=True)
class PipelineStep:
    subtask: SubtaskSpec
    provider: str
    result: ProviderResult
    agent_id: str


class ResearchPipeline:
    """Run decomposed work with role-matched agents and optional durable storage."""

    def __init__(
        self,
        engine: SSSWETEngine | None = None,
        provider: ResearchProvider | None = None,
        store: SQLiteResearchStore | None = None,
    ):
        self.engine = engine or SSSWETEngine()
        self.decomposer = TaskDecomposer()
        self.groups = GroupManager()
        self.provider = provider or DeterministicDemoProvider()
        self.store = store

    def start(self, objective: str, domain: str = "general") -> tuple[str, list[PipelineStep]]:
        task = self.engine.submit(objective, domain)
        event_start = len(self.engine.orchestrator.events) - 1
        subtasks = self.decomposer.decompose(objective, domain)
        agents: list[Agent] = []
        results: list[PipelineStep] = []

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

            for subtask, agent in zip(subtasks, agents, strict=True):
                result = self.provider.investigate(subtask.objective, "initial")
                results.append(PipelineStep(subtask, self.provider.name, result, agent.id))
                self.engine.orchestrator.events.append(ResearchEvent(
                    "research_pass",
                    f"{agent.role} completed a research pass; evidence remains subject to verification.",
                    task.id,
                    agent.id,
                ))

            # Provider output is not automatically promoted to a verified finding.
            self.engine.orchestrator.complete(task, agents[0].id, accepted=True)
            self.engine.orchestrator.release_team(agents[1:], completed=True)
            if self.store:
                self.store.save_run(task, self.engine.orchestrator.events[event_start:], results)
            return task.id, results
        except Exception:
            if agents:
                self.engine.orchestrator.release_team(agents)
            if task.status != TaskStatus.QUEUED:
                task.status = TaskStatus.BLOCKED
                if task not in self.engine.orchestrator.tasks:
                    self.engine.orchestrator.tasks.append(task)
                self.engine.orchestrator.events.append(ResearchEvent(
                    "pipeline_blocked",
                    "Work was preserved in the queue after a provider or allocation failure.",
                    task.id,
                ))
            if self.store:
                self.store.save_run(task, self.engine.orchestrator.events[event_start:], results)
            raise
