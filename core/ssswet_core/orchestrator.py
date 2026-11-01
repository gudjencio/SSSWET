from collections import deque
from uuid import uuid4

from .models import Agent, AgentStatus, ResearchEvent, Task, TaskStatus


class BotManager:
    def __init__(self, max_agents: int = 24):
        self.max_agents = max_agents
        self.agents: dict[str, Agent] = {}

    def ensure_capacity(self, required: int = 1) -> list[Agent]:
        created: list[Agent] = []
        while len(self.agents) < min(self.max_agents, required + len(self.agents)):
            number = len(self.agents) + 1
            agent = Agent(id=f"bot-{number:03d}", role="researcher")
            self.agents[agent.id] = agent
            created.append(agent)
            if len(created) >= required:
                break
        return created

    def available(self) -> list[Agent]:
        return [a for a in self.agents.values() if a.status == AgentStatus.WAITING]

    def retire_idle(self) -> None:
        waiting = self.available()
        for agent in waiting[2:]:
            agent.status = AgentStatus.RETIRED


class ResearchOrchestrator:
    def __init__(self):
        self.tasks: deque[Task] = deque()
        self.bot_manager = BotManager()
        self.events: list[ResearchEvent] = []

    def submit(self, objective: str, domain: str = "general", priority: int = 5) -> Task:
        task = Task(id=str(uuid4()), objective=objective, domain=domain, priority=priority)
        self.tasks.append(task)
        self.events.append(ResearchEvent("task_created", "New research task queued.", task.id))
        self.bot_manager.ensure_capacity(1)
        return task

    def schedule(self) -> list[tuple[str, str]]:
        assignments: list[tuple[str, str]] = []
        for agent in self.bot_manager.available():
            if not self.tasks:
                break
            task = self.tasks.popleft()
            task.status = TaskStatus.ACTIVE
            task.attempts += 1
            agent.status = AgentStatus.WORKING
            agent.load = 1.0
            agent.current_task = task.id
            assignments.append((agent.id, task.id))
            self.events.append(ResearchEvent("task_assigned", "Task assigned to a research bot.", task.id, agent.id))
        return assignments

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
                }
                for a in self.bot_manager.agents.values()
            ],
        }
