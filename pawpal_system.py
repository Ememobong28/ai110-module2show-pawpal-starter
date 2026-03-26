import json
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date, timedelta


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str              # "low", "medium", or "high"
    frequency: str = "daily"   # "daily", "weekly", "as-needed"
    completed: bool = False
    due_date: Optional[date] = None
    start_time: Optional[str] = None   # "HH:MM" — set when user wants a fixed slot

    def __post_init__(self):
        """Default due_date to today if not provided."""
        if self.due_date is None:
            self.due_date = date.today()

    def priority_value(self) -> int:
        """Convert priority label to a number so tasks can be sorted."""
        mapping = {"high": 3, "medium": 2, "low": 1}
        return mapping.get(self.priority, 0)

    def weighted_score(self) -> float:
        """
        Challenge 1 — weighted prioritization.
        Score = priority points + overdue bonus + frequency urgency bonus.
        Higher score → scheduled earlier.
          - Overdue tasks gain +2 per day past due (capped at +10).
          - Daily tasks gain +1 over weekly; as-needed tasks get no bonus.
        """
        base = self.priority_value() * 10
        days_overdue = max(0, (date.today() - self.due_date).days)
        overdue_bonus = min(days_overdue * 2, 10)
        frequency_bonus = {"daily": 1, "weekly": 0, "as-needed": 0}.get(self.frequency, 0)
        return base + overdue_bonus + frequency_bonus

    def mark_complete(self):
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self):
        """Reset this task to not done."""
        self.completed = False

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh Task due on the next occurrence date, or None if not recurring."""
        if self.frequency == "daily":
            next_due = date.today() + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = date.today() + timedelta(weeks=1)
        else:
            return None
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            due_date=next_due,
        )

    def to_dict(self) -> dict:
        """Serialize this task to a plain dictionary for JSON storage."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "completed": self.completed,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "start_time": self.start_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Reconstruct a Task from a plain dictionary."""
        due = date.fromisoformat(data["due_date"]) if data.get("due_date") else None
        return cls(
            title=data["title"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            frequency=data.get("frequency", "daily"),
            completed=data.get("completed", False),
            due_date=due,
            start_time=data.get("start_time"),
        )


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

    def complete_task(self, title: str):
        """Mark a task complete; if it recurs, append the next occurrence immediately."""
        for task in self.tasks:
            if task.title == title and not task.completed:
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task:
                    self.tasks.append(next_task)
                break

    def to_dict(self) -> dict:
        """Serialize this pet to a plain dictionary for JSON storage."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Reconstruct a Pet from a plain dictionary."""
        pet = cls(name=data["name"], species=data["species"])
        pet.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return pet


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

    def filter_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks belonging to a specific pet by name."""
        for pet in self.pets:
            if pet.name == pet_name:
                return list(pet.tasks)
        return []

    def filter_tasks_by_status(self, completed: bool) -> List[Task]:
        """Return tasks across all pets that match the given completion status."""
        return [t for t in self.get_all_tasks() if t.completed == completed]

    def to_dict(self) -> dict:
        """Serialize the owner (and all nested pets/tasks) to a plain dictionary."""
        return {
            "name": self.name,
            "available_minutes": self.available_minutes,
            "pets": [p.to_dict() for p in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Reconstruct an Owner (and all nested pets/tasks) from a plain dictionary."""
        owner = cls(name=data["name"], available_minutes=data["available_minutes"])
        owner.pets = [Pet.from_dict(p) for p in data.get("pets", [])]
        return owner

    def save_to_json(self, filepath: str = "data.json"):
        """Persist the owner's full state to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> "Owner":
        """Load and reconstruct an Owner from a JSON file."""
        with open(filepath) as f:
            return cls.from_dict(json.load(f))


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

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks shortest-first within the same priority level."""
        return sorted(tasks, key=lambda t: t.duration_minutes)

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """
        Check for tasks with overlapping fixed start times.
        Returns a list of warning strings; empty list means no conflicts.
        """
        warnings = []
        timed = [t for t in tasks if t.start_time is not None]

        for i, a in enumerate(timed):
            for b in timed[i + 1:]:
                a_start = self._time_to_minutes(a.start_time)
                a_end = a_start + a.duration_minutes
                b_start = self._time_to_minutes(b.start_time)
                b_end = b_start + b.duration_minutes

                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"Conflict: '{a.title}' ({a.start_time}, {a.duration_minutes} min) "
                        f"overlaps with '{b.title}' ({b.start_time}, {b.duration_minutes} min)"
                    )
        return warnings

    @staticmethod
    def _time_to_minutes(time_str: str) -> int:
        """Convert 'HH:MM' string to total minutes since midnight."""
        h, m = map(int, time_str.split(":"))
        return h * 60 + m

    def generate(self) -> Schedule:
        """
        Challenge 1 — weighted prioritization.
        Sort by weighted_score() (priority + overdue bonus + frequency bonus),
        break ties by shortest duration first. Greedily fill available time.
        """
        tasks = sorted(
            self.get_tasks(),
            key=lambda t: (t.weighted_score(), -t.duration_minutes),
            reverse=True,
        )

        conflicts = self.detect_conflicts(tasks)
        for warning in conflicts:
            print(f"  WARNING: {warning}")

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
