from dataclasses import dataclass

from .models import Agent


@dataclass(frozen=True)
class ResearchGroup:
    id: str
    task_id: str
    members: tuple[str, ...]
    purpose: str


class GroupManager:
    def __init__(self) -> None:
        self.groups: dict[str, ResearchGroup] = {}
        self._counter = 0

    def create(self, task_id: str, agents: list[Agent], purpose: str) -> ResearchGroup:
        self._counter += 1
        group = ResearchGroup(
            id=f"group-{self._counter:03d}",
            task_id=task_id,
            members=tuple(agent.id for agent in agents),
            purpose=purpose,
        )
        self.groups[group.id] = group
        return group

    def for_task(self, task_id: str) -> list[ResearchGroup]:
        return [group for group in self.groups.values() if group.task_id == task_id]
