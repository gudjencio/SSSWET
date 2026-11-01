from collections import deque
from uuid import uuid4

from .models import Agent, AgentStatus, ResearchEvent, Task, TaskStatus
from .strategies import StrategySelector


class BotManager:
    def __init__(self, max_agents: int = 24):
        self.max_agents = max_agents
        self.agents: dict[str, Agent] = {}
        self._next_id = 1

    def _new_agent(self, role: str = "researcher") -> Agent:
        agent = Agent(id=f"bot-{self._next_id:03d}", role=role)
        self._next_id += 1
        self.agents[agent.id] = agent
        return agent

    def ensure_capacity(self, required: int = 1) -> list[Agent]:
        created: list[Agent] = []
        target = min(self.max_agents, len(self.agents) + max(1, required))
        while len(self.agents) < target:
            created.append(self._new_agent())
        return created

    def ensure_role_capacity(self, roles: list[str]) -> list[Agent]:
        """Return one waiting agent per requested role, creating only as needed."""
        selected: list[Agent] = []
        waiting = self.available()
        for role in roles:
            candidate = next((a for a in waiting if a.role == role), None)
            if candidate is None:
                candidate = next((a for a in waiting if a.role == "researcher"), None)
                if candidate is not None:
                    candidate.role = role
            if candidate is None and len(self.agents) < self.max_agents:
                candidate = self._new_agent(role)
            if candidate is None:
                raise RuntimeError("Agent capacity exhausted; team was not fully allocated.")
            if candidate in waiting:
                waiting.remove(candidate)
            selected.append(candidate)
        return selected

    def available(self) -> list[Agent]:
        return [a for a in self.agents.values() if a.status == AgentStatus.WAITING]

    def release(self, agent_id: str, completed: bool = False) -> None:
        agent = self.agents[agent_id]
        agent.status = AgentStatus.WAITING
        agent.load = 0.0
        agent.current_task = None
        if completed:
            agent.completed_tasks += 1

    def retire_idle(self, keep: int = 2) -> None:
        waiting = self.available()
        for agent in waiting[keep:]:
            agent.status = AgentStatus.RETIRED


class ResearchOrchestrator:
    def __init__(self, max_agents: int = 24):
        self.tasks: deque[Task] = deque()
        self.bot_manager = BotManager(max_agents=max_agents)
        self.events: list[ResearchEvent] = []
        self.strategies = StrategySelector()

    def submit(self, objective: str, domain: str = "general", priority: int = 5) -> Task:
        task = Task(id=str(uuid4()), objective=objective, domain=domain, priority=priority)
        self.tasks.append(task)
        self.events.append(ResearchEvent("task_created", "New research task queued.", task.id))
        self.bot_manager.ensure_capacity(1)
        return task

    def assign_team(self, task: Task, roles: list[str]) -> list[Agent]:
        """Allocate and activate a specialist team for one parent research task."""
        agents = self.bot_manager.ensure_role_capacity(roles)
        if task in self.tasks:
            self.tasks.remove(task)
        task.status = TaskStatus.ACTIVE
        task.attempts += 1
        strategy = self.strategies.next(task.strategy_history)
        task.strategy_history.append(strategy.name)
        for agent in agents:
            agent.status = AgentStatus.WORKING
            agent.load = 1.0
            agent.current_task = task.id
            self.events.append(ResearchEvent(
                "agent_assigned",
                f"Specialist role {agent.role} assigned using strategy: {strategy.name}.",
                task.id,
                agent.id,
            ))
        self.events.append(ResearchEvent(
            "team_created",
            f"Specialist team allocated: {len(agents)} agents.",
            task.id,
        ))
        return agents

    def release_team(self, agents: list[Agent], completed: bool = False) -> None:
        for agent in agents:
            if agent.id in self.bot_manager.agents and agent.load > 0:
                self.bot_manager.release(agent.id, completed=completed)

    def schedule(self) -> list[tuple[str, str]]:
        assignments: list[tuple[str, str]] = []
        if self.tasks:
            self.bot_manager.ensure_capacity(min(len(self.tasks), self.bot_manager.max_agents))
        available = self.bot_manager.available()
        while available and self.tasks:
            task = self.tasks.popleft()
            agent = available.pop(0)
            task.status = TaskStatus.ACTIVE
            task.attempts += 1
            strategy = self.strategies.next(task.strategy_history)
            task.strategy_history.append(strategy.name)
            agent.status = AgentStatus.WORKING
            agent.load = 1.0
            agent.current_task = task.id
            assignments.append((agent.id, task.id))
            self.events.append(ResearchEvent("task_assigned", f"Task assigned using strategy: {strategy.name}.", task.id, agent.id))
        return assignments

    def mark_blocked(self, task: Task, agent_id: str) -> None:
        task.status = TaskStatus.BLOCKED
        self.tasks.append(task)
        self.bot_manager.release(agent_id)
        self.events.append(ResearchEvent("task_blocked", "Task preserved and returned to the queue for a different strategy.", task.id, agent_id))

    def complete(self, task: Task, agent_id: str, accepted: bool = True) -> None:
        task.status = TaskStatus.COMPLETE if accepted else TaskStatus.REJECTED
        self.bot_manager.release(agent_id, completed=accepted)
        self.events.append(ResearchEvent("task_completed" if accepted else "task_rejected", "Task lifecycle state updated.", task.id, agent_id))

    def checkpoint(self) -> dict:
        return {
            "queued_tasks": len(self.tasks),
            "agents": [
                {
                    "id": a.id,
                    "role": a.role,
                    "status": a.status.value,
                    "load": a.load,
                    "current_task": a.current_task,
                    "completed_tasks": a.completed_tasks,
                }
                for a in self.bot_manager.agents.values()
            ],
        }
