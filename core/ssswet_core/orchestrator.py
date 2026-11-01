from collections import deque
from uuid import uuid4

from .models import Agent, AgentStatus, ResearchEvent, Task, TaskStatus
from .strategies import StrategySelector


class BotManager:
    def __init__(self, max_agents: int = 24):
        self.max_agents = max_agents
        self.agents: dict[str, Agent] = {}

    def ensure_capacity(self, required: int = 1) -> list[Agent]:
        created: list[Agent] = []
        target = min(self.max_agents, len(self.agents) + max(1, required))
        while len(self.agents) < target:
            number = len(self.agents) + 1
            agent = Agent(id=f"bot-{number:03d}", role="researcher")
            self.agents[agent.id] = agent
            created.append(agent)
        return created

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
