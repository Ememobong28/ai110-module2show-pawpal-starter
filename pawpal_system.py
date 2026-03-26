from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str        # "low", "medium", or "high"
    frequency: str = "daily"   # "daily", "weekly", "as-needed"
    completed: bool = False

    def priority_value(self) -> int:
        """Convert priority label to a number so tasks can be sorted."""
        mapping = {"high": 3, "medium": 2, "low": 1}
        return mapping.get(self.priority, 0)

    def mark_complete(self):
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self):
        """Reset this task to not done."""
        self.completed = False


@dataclass
class Pet:
    name: str
    species: str         # "dog", "cat", or "other"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str):
        """Remove a task from this pet's list by title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def pending_tasks(self) -> List[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]


class Owner:
    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, name: str):
        """Remove a pet from this owner's list by name."""
        self.pets = [p for p in self.pets if p.name != name]

    def get_all_tasks(self) -> List[Task]:
        """Collect every task across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_pending_tasks(self) -> List[Task]:
        """Collect only incomplete tasks across all pets."""
        pending = []
        for pet in self.pets:
            pending.extend(pet.pending_tasks())
        return pending


class Schedule:
    def __init__(self):
        self.planned_tasks: List[Task] = []
        self.skipped_tasks: List[Task] = []
        self.total_duration: int = 0

    def summary(self) -> str:
        """Return a plain-language explanation of the plan."""
        if not self.planned_tasks and not self.skipped_tasks:
            return "No tasks to schedule."

        lines = []

        if self.planned_tasks:
            lines.append(f"Scheduled ({self.total_duration} min total):")
            for task in self.planned_tasks:
                lines.append(
                    f"  - {task.title} ({task.duration_minutes} min, {task.priority} priority)"
                )

        if self.skipped_tasks:
            lines.append("Skipped (not enough time remaining):")
            for task in self.skipped_tasks:
                lines.append(
                    f"  - {task.title} ({task.duration_minutes} min, {task.priority} priority)"
                )

        return "\n".join(lines)


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def get_tasks(self) -> List[Task]:
        """Ask the Owner for all pending tasks across its pets."""
        return self.owner.get_pending_tasks()

    def generate(self) -> Schedule:
        """
        Sort pending tasks by priority (highest first), then greedily fit
        them into the owner's available time. Tasks that don't fit are skipped.
        """
        tasks = sorted(self.get_tasks(), key=lambda t: t.priority_value(), reverse=True)
        schedule = Schedule()
        time_remaining = self.owner.available_minutes

        for task in tasks:
            if task.duration_minutes <= time_remaining:
                schedule.planned_tasks.append(task)
                schedule.total_duration += task.duration_minutes
                time_remaining -= task.duration_minutes
            else:
                schedule.skipped_tasks.append(task)

        return schedule
