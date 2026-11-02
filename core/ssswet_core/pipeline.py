from concurrent.futures import ThreadPoolExecutor, as_completed
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
                resource_state = self.campaign_coordinator.snapshot()
                if any(task_id in resource_state["failed_task_ids"] for task_id in task_ids):
                    self.campaign_coordinator.block_milestone(
                        campaign_id,
                        milestone_id,
                        "At least one required work item exhausted its retry policy; operator review is required.",
                    )
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

    def start(self, objective: str, domain: str = "general", progress_callback=None) -> tuple[str, list[PipelineStep]]:
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

            active_by_id: dict[str, dict] = {}
            completed_steps: dict[int, PipelineStep] = {}
            indexed_futures = {}
            worker_count = max(1, min(6, len(subtasks)))
            with ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="ssswet-agent") as executor:
                for index, (subtask, agent) in enumerate(zip(subtasks, agents, strict=True)):
                    active_by_id[agent.id] = {
                        "id": agent.id,
                        "role": agent.role,
                        "task_id": task.id,
                        "objective": subtask.objective,
                        "phase": "literature_search",
                        "activity": "Searching Crossref and OpenAlex scholarly literature",
                    }
                    future = executor.submit(self.provider.investigate, subtask.objective, "initial")
                    indexed_futures[future] = (index, subtask, agent)
                    if progress_callback:
                        progress_callback({
                            "phase": "agent_working",
                            "task_id": task.id,
                            "active_agents": list(active_by_id.values()),
                        })

                for future in as_completed(indexed_futures):
                    index, subtask, agent = indexed_futures[future]
                    result = future.result()
                    completed_steps[index] = PipelineStep(subtask, self.provider.name, result, agent.id)
                    self.engine.orchestrator.events.append(ResearchEvent(
                        "research_pass",
                        f"{agent.role} completed a research pass; evidence remains subject to verification.",
                        task.id,
                        agent.id,
                    ))
                    active_by_id.pop(agent.id, None)
                    if progress_callback:
                        progress_callback({
                            "phase": "agent_pass_completed",
                            "task_id": task.id,
                            "active_agents": list(active_by_id.values()),
                            "last_agent": {"id": agent.id, "role": agent.role},
                        })

            results.extend(completed_steps[index] for index in sorted(completed_steps))

            # Share outputs, then let each recipient run one independent literature
            # check on a teammate's work. A review is a research lead, never approval.
            if self.store and len(results) > 1:
                handoffs = []
                for index, sender in enumerate(results):
                    recipient = results[(index + 1) % len(results)]
                    summary = sender.result.summary.strip()
                    if not summary:
                        continue
                    message_id = self.store.publish_agent_message(
                        task_id=task.id,
                        sender_agent_id=sender.agent_id,
                        sender_role=sender.subtask.role,
                        recipient_agent_id=recipient.agent_id,
                        recipient_role=recipient.subtask.role,
                        message_type="peer_review_request",
                        content=(
                            "Independent review requested. Examine this unverified teammate output; "
                            "do not assume it is correct: " + summary[:3000]
                        ),
                    )
                    handoffs.append((message_id, sender, recipient))

                review_active = {}
                review_futures = {}
                review_workers = max(1, min(4, len(handoffs)))
                with ThreadPoolExecutor(max_workers=review_workers, thread_name_prefix="ssswet-review") as executor:
                    for message_id, sender, reviewer in handoffs:
                        original = self.store.agent_message(message_id)
                        if not original:
                            continue
                        review_objective = (
                            "Independently search for scholarly literature relevant to this research "
                            "output. Look for evidence that could support, qualify, or challenge it. "
                            "Do not infer agreement from search results. Original task: "
                            + task.objective[:900]
                            + ". Teammate output: "
                            + str(original["content"])[-3000:]
                        )
                        review_active[reviewer.agent_id] = {
                            "id": reviewer.agent_id,
                            "role": reviewer.subtask.role,
                            "task_id": task.id,
                            "objective": "Independently checking a teammate's provisional research output",
                            "phase": "independent_review",
                            "activity": "Cross-checking a teammate's output against scholarly literature",
                        }
                        future = executor.submit(
                            self.provider.investigate, review_objective, "independent_peer_review"
                        )
                        review_futures[future] = (message_id, sender, reviewer)
                        if progress_callback:
                            progress_callback({
                                "phase": "peer_review_working",
                                "task_id": task.id,
                                "active_agents": list(review_active.values()),
                            })

                    for future in as_completed(review_futures):
                        message_id, sender, reviewer = review_futures[future]
                        try:
                            review_result = future.result()
                            evidence_text = " | ".join(review_result.evidence[:4])
                            response = (
                                f"Review of handoff #{message_id}. Independent literature-search pass "
                                f"completed by {reviewer.subtask.role}. {review_result.summary[:1800]} "
                                f"Evidence leads: {evidence_text[:2200] or 'No usable evidence leads returned.'} "
                                f"Uncertainty: {review_result.uncertainty:.2f}. "
                                "Assessment remains provisional; this is not approval or verification."
                            )
                            self.store.publish_agent_message(
                                task_id=task.id,
                                sender_agent_id=reviewer.agent_id,
                                sender_role=reviewer.subtask.role,
                                recipient_agent_id=sender.agent_id,
                                recipient_role=sender.subtask.role,
                                message_type="peer_review_response",
                                content=response[:4000],
                            )
                            self.engine.orchestrator.events.append(ResearchEvent(
                                "peer_review_completed",
                                "A teammate's output received an independent literature-search review; no approval was implied.",
                                task.id,
                                reviewer.agent_id,
                            ))
                        except Exception as error:
                            self.engine.orchestrator.events.append(ResearchEvent(
                                "peer_review_blocked",
                                f"An independent peer-review search could not complete ({type(error).__name__}); the original output remains unverified.",
                                task.id,
                                reviewer.agent_id,
                            ))
                        finally:
                            review_active.pop(reviewer.agent_id, None)
                            if progress_callback:
                                progress_callback({
                                    "phase": "peer_review_progress",
                                    "task_id": task.id,
                                    "active_agents": list(review_active.values()),
                                    "last_agent": {"id": reviewer.agent_id, "role": reviewer.subtask.role},
                                })

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
