"""PawPal+ core system.

A small, beginner-readable domain model for planning daily pet-care tasks.
Four classes only: Owner, Pet, Task, Scheduler.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Priority is a number where a lower value means higher priority.
HIGH, MEDIUM, LOW = 1, 2, 3
VALID_PRIORITIES = (HIGH, MEDIUM, LOW)


@dataclass
class Task:
    """A single pet-care activity, e.g. a 30-minute walk."""

    name: str  # description of the activity
    duration: int  # minutes (the "time" the task takes)
    priority: int  # 1 = high, 2 = medium, 3 = low
    category: str = "general"

    frequency: str = "daily"  # e.g. "daily", "weekly"
    completion_status: bool = False  # True once the task is done

    def __post_init__(self) -> None:
        """Normalize the task name after the dataclass is created."""
        # Normalize the name so duplicate checks can't be bypassed by stray spaces.
        self.name = self.name.strip()

    def mark_done(self) -> None:
        """Mark this task as completed."""
        self.completion_status = True

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.mark_done()

    def mark_pending(self) -> None:
        """Mark this task as not yet done (e.g. resetting for a new day)."""
        self.completion_status = False

    def update_duration(self, duration: int) -> None:
        """Set a new duration after checking it is positive."""
        if duration <= 0:
            raise ValueError("Duration must be a positive number of minutes")
        self.duration = duration

    def update_priority(self, priority: int) -> None:
        """Set a new priority, restricted to the allowed values."""
        if priority not in VALID_PRIORITIES:
            raise ValueError("Priority must be 1 (high), 2 (medium) or 3 (low)")
        self.priority = priority

    def is_valid(self) -> bool:
        """Return True only if every field holds a sensible value."""
        return (
            bool(self.name.strip())
            and self.duration > 0
            and self.priority in VALID_PRIORITIES
        )


@dataclass
class Pet:
    """A pet that owns an ordered list of care tasks."""

    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize the pet name after the dataclass is created."""
        self.name = self.name.strip()

    def task_exists(self, name: str) -> bool:
        """Return True if a task with this name (case-insensitive) is present."""
        name = name.strip().lower()
        return any(task.name.lower() == name for task in self.tasks)

    def add_task(self, task: Task) -> None:
        """Add a task, rejecting invalid tasks and duplicate names."""
        if not task.is_valid():
            raise ValueError("cannot add an invalid task")
        if self.task_exists(task.name):
            raise ValueError(f"task '{task.name}' already exists for {self.name}")
        self.tasks.append(task)

    def remove_task(self, name: str) -> None:
        """Remove the task with the given name."""
        if not self.task_exists(name):
            raise ValueError(f"no task named '{name}' for {self.name}")
        target = name.strip().lower()
        self.tasks = [t for t in self.tasks if t.name.lower() != target]

    def get_tasks(self) -> list[Task]:
        """Return this pet's list of tasks."""
        return self.tasks


@dataclass
class Owner:
    """A person who owns pets and has a daily time budget for care."""

    name: str
    available_time: int  # minutes available per day
    preferences: dict[str, str] = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize the owner name after the dataclass is created."""
        self.name = self.name.strip()

    def pet_exists(self, name: str) -> bool:
        """Return True if a pet with this name (case-insensitive) is present."""
        name = name.strip().lower()
        return any(pet.name.lower() == name for pet in self.pets)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet, rejecting empty names and duplicates."""
        if not pet.name.strip():
            raise ValueError("pet name cannot be empty")
        if self.pet_exists(pet.name):
            raise ValueError(f"pet '{pet.name}' already exists")
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove the pet with the given name."""
        if not self.pet_exists(name):
            raise ValueError(f"no pet named '{name}'")
        target = name.strip().lower()
        self.pets = [p for p in self.pets if p.name.lower() != target]

    def get_pets(self) -> list[Pet]:
        """Return this owner's list of pets."""
        return self.pets

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets, in pet order then task order."""
        return [task for pet in self.pets for task in pet.get_tasks()]

    def set_preferences(self, preferences: dict[str, str]) -> None:
        """Replace this owner's preferences with the given dictionary."""
        self.preferences = preferences


@dataclass
class Scheduler:
    """Builds an explainable daily plan from tasks within a time budget."""

    tasks: list[Task] = field(default_factory=list)
    daily_plan: list[Task] = field(default_factory=list)

    @classmethod
    def from_pet(cls, pet: Pet) -> "Scheduler":
        """Build a scheduler for a single pet's tasks (the Pet -> Scheduler link)."""
        return cls(tasks=pet.get_tasks())

    @classmethod
    def from_owner(cls, owner: Owner) -> "Scheduler":
        """Build a scheduler from every task across all of an owner's pets."""
        return cls(tasks=owner.get_all_tasks())

    def sort_tasks_by_priority(self) -> list[Task]:
        """Return tasks ordered by priority (high first), keeping input order on ties."""
        # sorted() is stable, so equal-priority tasks stay in their original order.
        return sorted(self.tasks, key=lambda task: task.priority)

    def generate_daily_plan(self, owner: Owner) -> list[Task]:
        """Fill the day with the highest-priority tasks that fit the owner's time.

        Walks the sorted tasks once and greedily keeps each task whose duration
        still fits in the remaining time budget.
        """
        if not self.tasks:
            raise ValueError("no tasks available to schedule")
        if owner.available_time <= 0:
            raise ValueError("owner has no available time")

        remaining = owner.available_time
        plan: list[Task] = []
        for task in self.sort_tasks_by_priority():
            if not task.is_valid():
                continue  # ignore malformed tasks added directly to self.tasks
            if task.completion_status:
                continue  # already done today, no need to schedule it
            if task.duration <= remaining:
                plan.append(task)
                remaining -= task.duration
        self.daily_plan = plan
        return plan

    def validate_schedule(self, owner: Owner) -> bool:
        """Return True if the current plan is valid and fits the time budget."""
        total = sum(task.duration for task in self.daily_plan)
        return all(task.is_valid() for task in self.daily_plan) and total <= owner.available_time

    def explain_plan(self) -> str:
        """Return a human-readable summary of the scheduled tasks."""
        if not self.daily_plan:
            return "No tasks scheduled."
        labels = {HIGH: "high", MEDIUM: "medium", LOW: "low"}
        lines = [
            f"- {task.name}: {task.duration} min ({labels[task.priority]} priority)"
            for task in self.daily_plan
        ]
        total = sum(task.duration for task in self.daily_plan)
        lines.append(f"Total: {total} min across {len(self.daily_plan)} task(s).")
        return "\n".join(lines)
