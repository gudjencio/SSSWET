from dataclasses import dataclass

from .decomposer import SubtaskSpec, TaskDecomposer
from .engine import SSSWETEngine
from .groups import GroupManager
from .models import Agent, ResearchEvent, TaskStatus
from .persistence import SQLiteResearchStore
from .providers import DeterministicDemoProvider, ProviderResult, ResearchProvider
from .campaign_coordinator import CampaignCoordinator


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
        campaign_coordinator: CampaignCoordinator | None = None,
    ):
        self.engine = engine or SSSWETEngine()
        self.decomposer = TaskDecomposer()
        self.groups = GroupManager()
        self.provider = provider or DeterministicDemoProvider()
        self.store = store
        self.campaign_coordinator = campaign_coordinator

    def start_in_campaign(
        self,
        objective: str,
        campaign_id: str,
        milestone_id: str,
        domain: str = "general",
    ) -> tuple[str, list[PipelineStep]]:
        """Execute decomposed provider work through a campaign resource queue."""
        if self.campaign_coordinator is None:
            raise RuntimeError("A campaign coordinator must be configured")

        task = self.engine.submit(objective, domain)
        event_start = len(self.engine.orchestrator.events) - 1
        subtasks = self.decomposer.decompose(objective, domain)
        task_ids = self.campaign_coordinator.queue_subtasks(
            campaign_id, milestone_id, task.id, subtasks
        )
        if task in self.engine.orchestrator.tasks:
            self.engine.orchestrator.tasks.remove(task)
        task.status = TaskStatus.ACTIVE
        self.engine.orchestrator.events.append(ResearchEvent(
            "campaign_work_queued",
            "Decomposed research work was queued under the selected campaign milestone.",
            task.id,
        ))

        subtask_by_id = {
            task_id: subtask for task_id, subtask in zip(task_ids, subtasks, strict=True)
        }
        results: list[PipelineStep] = []
        used_agents: dict[str, Agent] = {}
        finished_ids: set[str] = set()
        maximum_cycles = len(subtasks) * self.campaign_coordinator.resources.max_attempts + 1

        try:
            for _ in range(maximum_cycles):
                if len(finished_ids) == len(task_ids):
                    break
                assignments = self.campaign_coordinator.dispatch()
                if not assignments:
                    break
                for assignment in assignments:
                    request_id = assignment.request.task_id
                    subtask = subtask_by_id[request_id]
                    agent = self.campaign_coordinator.resources.bot_manager.agents[assignment.agent_id]
                    used_agents[agent.id] = agent
                    try:
                        result = self.provider.investigate(subtask.objective, "initial")
                    except Exception as error:
                        self.campaign_coordinator.finish(request_id, success=False)
                        self.engine.orchestrator.events.append(ResearchEvent(
                            "campaign_research_attempt_failed",
                            f"A provider attempt failed ({type(error).__name__}); retry policy applied.",
                            task.id,
                            agent.id,
                        ))
                        state = self.campaign_coordinator.snapshot()
                        if request_id in state["failed_task_ids"]:
                            finished_ids.add(request_id)
                        continue

                    results.append(PipelineStep(subtask, self.provider.name, result, agent.id))
                    self.campaign_coordinator.finish(request_id, success=True)
                    finished_ids.add(request_id)
                    self.engine.orchestrator.events.append(ResearchEvent(
                        "campaign_research_pass",
                        f"{subtask.role} completed a provider pass; output remains subject to verification.",
                        task.id,
                        agent.id,
                    ))

            if used_agents:
                self.groups.create(
                    task.id, list(used_agents.values()),
                    "campaign milestone research and independent verification",
                )
            all_completed = all(
                task_id in self.campaign_coordinator.snapshot()["completed_task_ids"]
                for task_id in task_ids
            )
            if all_completed:
                task.status = TaskStatus.COMPLETE
                self.engine.orchestrator.events.append(ResearchEvent(
                    "task_completed",
                    "Campaign work batch completed; scientific verification remains separate.",
                    task.id,
                ))
            else:
                task.status = TaskStatus.BLOCKED
                self.engine.orchestrator.tasks.append(task)
                self.engine.orchestrator.events.append(ResearchEvent(
                    "campaign_work_blocked",
                    "Campaign work remains queued or exhausted its retry policy.",
                    task.id,
                ))
            if self.store:
                self.store.save_run(task, self.engine.orchestrator.events[event_start:], results)
            return task.id, results
        except Exception:
            task.status = TaskStatus.BLOCKED
            if task not in self.engine.orchestrator.tasks:
                self.engine.orchestrator.tasks.append(task)
            if self.store:
                self.store.save_run(task, self.engine.orchestrator.events[event_start:], results)
            raise

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
