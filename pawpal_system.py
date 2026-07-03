"""PawPal+ core system.

A small, beginner-readable domain model for planning daily pet-care tasks.
Four classes only: Owner, Pet, Task, Scheduler.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta

# Priority is a number where a lower value means higher priority.
HIGH, MEDIUM, LOW = 1, 2, 3
VALID_PRIORITIES = (HIGH, MEDIUM, LOW)

# Frequencies the scheduler understands for recurring tasks.
VALID_FREQUENCIES = ("one-time", "daily", "weekly")

# A name must start with a letter and may contain letters, spaces, hyphens,
# apostrophes, and slashes (so titles like "Play / enrichment" are allowed).
# This rejects empty strings, numbers, and symbol-only junk.
_NAME_RE = re.compile(r"[A-Za-z][A-Za-z '\-/]*")


# --------------------------- Validation helpers ----------------------------
def clean_name(name: str) -> str:
    """Strip outer spaces and collapse extra inner spaces (keeps capitalization)."""
    return " ".join(name.split())


def compare_key(name: str) -> str:
    """Return a lowercase key for duplicate checks only (never shown to the user)."""
    return clean_name(name).lower()


def is_valid_name(name: str) -> bool:
    """Return True if the cleaned name has letters and only safe characters."""
    return bool(_NAME_RE.fullmatch(clean_name(name)))


# --------------------------- Display formatting -----------------------------
# Emoji indicators keep the CLI and Streamlit output friendly and scannable.
# They are pure presentation helpers — the scheduling logic never depends on them.
PRIORITY_LABELS = {HIGH: "🔴 High", MEDIUM: "🟡 Medium", LOW: "🟢 Low"}

# Keyed by the lowercase task title (see compare_key) so matching is forgiving.
TASK_EMOJIS = {
    "feeding": "🍽️",
    "morning walk": "🦮",
    "medication": "💊",
    "grooming": "🧼",
    "play / enrichment": "🎾",
    "clean litter box": "🧹",
    "vet appointment": "🏥",
}


def priority_label(priority: int) -> str:
    """Return a colored word for a priority (e.g. '🔴 High'), or the number if unknown."""
    return PRIORITY_LABELS.get(priority, str(priority))


def task_emoji(name: str) -> str:
    """Return an emoji for a known task title, or a paw print for anything else."""
    return TASK_EMOJIS.get(compare_key(name), "🐾")


def find_time_conflict(tasks: list["Task"], start_time: str) -> "Task | None":
    """Return the first task already at start_time (exact match), or None (O(n))."""
    for task in tasks:
        if task.start_time == start_time:
            return task
    return None


def _time_to_minutes(start_time: str) -> int:
    """Convert a 'HH:MM' string into minutes since midnight for sorting."""
    hours, minutes = start_time.split(":")
    return int(hours) * 60 + int(minutes)


def _is_valid_time(start_time: str) -> bool:
    """Return True if start_time is a well-formed 'HH:MM' 24-hour string."""
    try:
        hours, minutes = start_time.split(":")
        return 0 <= int(hours) < 24 and 0 <= int(minutes) < 60
    except (ValueError, AttributeError):
        return False


@dataclass
class Task:
    """A single pet-care activity, e.g. a 30-minute walk."""

    name: str  # description of the activity
    duration: int  # minutes (the "time" the task takes)
    priority: int  # 1 = high, 2 = medium, 3 = low

    start_time: str = "09:00"  # when the task begins, in "HH:MM" format
    category: str = "general"
    frequency: str = "daily"  # "one-time", "daily", or "weekly"
    completion_status: bool = False  # True once the task is done
    pet_name: str = ""  # set by Pet.add_task so the scheduler knows the owner pet

    def __post_init__(self) -> None:
        """Normalize the task name after the dataclass is created."""
        # Clean the name so duplicate checks can't be bypassed by stray spaces.
        self.name = clean_name(self.name)

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
            is_valid_name(self.name)
            and self.duration > 0
            and self.priority in VALID_PRIORITIES
            and _is_valid_time(self.start_time)
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
        self.name = clean_name(self.name)

    def task_exists(self, name: str) -> bool:
        """Return True if a task with this title (case-insensitive) is present."""
        key = compare_key(name)
        return any(compare_key(task.name) == key for task in self.tasks)

    def add_task(self, task: Task) -> None:
        """Add a task, rejecting invalid tasks and duplicate titles."""
        if not task.is_valid():
            raise ValueError("cannot add an invalid task")
        if self.task_exists(task.name):
            raise ValueError(f"task '{task.name}' already exists for {self.name}")
        # Tag the task with its pet so the scheduler can group/label by pet.
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, name: str) -> None:
        """Remove the task with the given title."""
        if not self.task_exists(name):
            raise ValueError(f"no task named '{name}' for {self.name}")
        target = compare_key(name)
        self.tasks = [t for t in self.tasks if compare_key(t.name) != target]

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
        self.name = clean_name(self.name)

    def pet_exists(self, name: str) -> bool:
        """Return True if a pet with this name (case-insensitive) is present."""
        key = compare_key(name)
        return any(compare_key(pet.name) == key for pet in self.pets)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet, rejecting invalid names and duplicates."""
        if not is_valid_name(pet.name):
            raise ValueError("pet name must be letters (spaces, hyphens, apostrophes ok)")
        if self.pet_exists(pet.name):
            raise ValueError(f"pet '{pet.name}' already exists")
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove the pet with the given name."""
        if not self.pet_exists(name):
            raise ValueError(f"no pet named '{name}'")
        target = compare_key(name)
        self.pets = [p for p in self.pets if compare_key(p.name) != target]

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

    def sort_by_time(self) -> list[Task]:
        """Return tasks ordered by start_time, earliest first (O(n log n))."""
        return sorted(self.tasks, key=lambda task: _time_to_minutes(task.start_time))

    def sort_by_priority_then_time(self) -> list[Task]:
        """Return tasks ordered by priority (HIGH first), then by start_time on ties.

        Sorting on the tuple (priority, minutes-since-midnight) does both passes in
        one sort: priority 1/2/3 puts HIGH before MEDIUM before LOW, and tasks that
        share a priority fall into chronological order. This is the "advanced"
        ordering the daily plan is built from.

        Time complexity: O(n log n) for the single sort.
        Space complexity: O(n) for the returned list.
        """
        return sorted(
            self.tasks,
            key=lambda task: (task.priority, _time_to_minutes(task.start_time)),
        )

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[Task]:
        """Return tasks matching an optional pet name and/or completion status (O(n))."""
        results = self.tasks
        if pet_name is not None:
            key = compare_key(pet_name)
            results = [t for t in results if compare_key(t.pet_name) == key]
        if completed is not None:
            results = [t for t in results if t.completion_status == completed]
        return list(results)

    def find_conflicts(self) -> list[str]:
        """Return warnings for tasks that share the exact same start_time (O(n))."""
        by_time: dict[str, list[Task]] = {}
        for task in self.tasks:
            by_time.setdefault(task.start_time, []).append(task)
        warnings = []
        for start_time, tasks in by_time.items():
            if len(tasks) > 1:
                titles = ", ".join(f"{t.pet_name}'s {t.name}" for t in tasks)
                warnings.append(f"Conflict at {start_time}: {titles}")
        return warnings

    def next_occurrence(
        self, task: Task, from_date: date | None = None
    ) -> tuple[date, Task] | None:
        """Return (next_date, new Task) for a daily/weekly task, or None if one-time."""
        if task.frequency not in ("daily", "weekly"):
            return None
        if from_date is None:
            from_date = date.today()
        step = timedelta(days=1) if task.frequency == "daily" else timedelta(weeks=1)
        next_task = Task(
            name=task.name,
            duration=task.duration,
            priority=task.priority,
            start_time=task.start_time,
            category=task.category,
            frequency=task.frequency,
        )
        next_task.pet_name = task.pet_name
        return from_date + step, next_task

    def generate_daily_plan(self, owner: Owner) -> list[Task]:
        """Fill the day with the highest-priority tasks that fit the owner's time.

        Walks the priority-then-time sorted tasks once and greedily keeps each
        task whose duration still fits in the remaining time budget. Ordering by
        (priority, start_time) means high-priority tasks are considered first, and
        same-priority tasks are considered in chronological order.
        """
        if not self.tasks:
            raise ValueError("no tasks available to schedule")
        if owner.available_time <= 0:
            raise ValueError("owner has no available time")

        remaining = owner.available_time
        plan: list[Task] = []
        for task in self.sort_by_priority_then_time():
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
        """Return a human-readable, time-ordered summary of the scheduled tasks."""
        if not self.daily_plan:
            return "No tasks scheduled."
        labels = {HIGH: "high", MEDIUM: "medium", LOW: "low"}
        ordered = sorted(self.daily_plan, key=lambda task: _time_to_minutes(task.start_time))
        lines = [
            f"- {task.start_time} | {task.pet_name or '?'} | {task.name}: "
            f"{task.duration} min ({labels[task.priority]} priority)"
            for task in ordered
        ]
        total = sum(task.duration for task in self.daily_plan)
        lines.append(f"Total: {total} min across {len(self.daily_plan)} task(s).")
        return "\n".join(lines)
