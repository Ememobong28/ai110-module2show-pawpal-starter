from dataclasses import dataclass, field
from typing import List


@dataclass
class Pet:
    name: str
    species: str  # "dog", "cat", or "other"


@dataclass
class Owner:
    name: str
    available_minutes: int
    pet: Pet = None


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"

    def priority_value(self) -> int:
        """Return priority as a number for sorting (high=3, medium=2, low=1)."""
        mapping = {"high": 3, "medium": 2, "low": 1}
        return mapping.get(self.priority, 0)


class Schedule:
    def __init__(self):
        self.planned_tasks: List[Task] = []
        self.skipped_tasks: List[Task] = []
        self.total_duration: int = 0

    def summary(self) -> str:
        """Return a plain-language explanation of the plan."""
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: List[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate(self) -> Schedule:
        """Sort tasks by priority, fit them into available time, return a Schedule."""
        pass
