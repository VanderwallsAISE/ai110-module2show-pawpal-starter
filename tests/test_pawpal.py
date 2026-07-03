from datetime import date

import pytest

from pawpal_system import (
    Owner,
    Pet,
    Task,
    Scheduler,
    HIGH,
    MEDIUM,
    LOW,
    clean_name,
    is_valid_name,
    find_time_conflict,
)


def test_task_completion_changes_status():
    task = Task(name="Feeding", duration=10, priority=HIGH)

    assert task.completion_status is False

    task.mark_complete()

    assert task.completion_status is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Roxa", species="dog", age=4)
    task = Task(name="Morning walk", duration=30, priority=HIGH)

    assert len(pet.get_tasks()) == 0

    pet.add_task(task)

    assert len(pet.get_tasks()) == 1


def test_scheduler_only_adds_tasks_that_fit_available_time():
    owner = Owner(name="Vanderwalls", available_time=40)
    pet = Pet(name="Roxa", species="dog", age=4)

    pet.add_task(Task(name="Walk", duration=30, priority=HIGH))
    pet.add_task(Task(name="Play", duration=20, priority=MEDIUM))
    pet.add_task(Task(name="Brush", duration=15, priority=LOW))

    owner.add_pet(pet)

    scheduler = Scheduler.from_owner(owner)
    plan = scheduler.generate_daily_plan(owner)

    assert len(plan) == 1
    assert plan[0].name == "Walk"
    assert sum(task.duration for task in plan) <= owner.available_time


# --------------------------- Phase 4 additions ---------------------------
def test_clean_name_collapses_spaces_and_keeps_case():
    assert clean_name("  Mochi   the   Cat ") == "Mochi the Cat"


def test_name_validation_rejects_numbers_and_junk():
    assert is_valid_name("Mary-Jane") is True
    assert is_valid_name("O'Brien") is True
    assert is_valid_name("Dog123") is False
    assert is_valid_name("!!!") is False
    assert is_valid_name("   ") is False


def test_add_pet_rejects_invalid_name():
    owner = Owner(name="Vanderwalls", available_time=60)
    with pytest.raises(ValueError):
        owner.add_pet(Pet(name="Pet7", species="dog", age=1))


def test_scheduler_sorts_tasks_by_time():
    pet = Pet(name="Roxa", species="dog", age=4)
    pet.add_task(Task(name="Evening walk", duration=20, priority=LOW, start_time="18:00"))
    pet.add_task(Task(name="Morning walk", duration=30, priority=HIGH, start_time="08:00"))
    pet.add_task(Task(name="Lunch", duration=10, priority=MEDIUM, start_time="12:30"))

    scheduler = Scheduler.from_pet(pet)
    times = [task.start_time for task in scheduler.sort_by_time()]

    assert times == ["08:00", "12:30", "18:00"]


def test_scheduler_sorts_by_priority_then_time():
    pet = Pet(name="Roxa", species="dog", age=4)
    # Two HIGH tasks added out of time order, plus a MEDIUM and a LOW.
    pet.add_task(Task(name="Evening meds", duration=5, priority=HIGH, start_time="20:00"))
    pet.add_task(Task(name="Morning meds", duration=5, priority=HIGH, start_time="07:00"))
    pet.add_task(Task(name="Lunch play", duration=20, priority=MEDIUM, start_time="12:00"))
    pet.add_task(Task(name="Brush", duration=15, priority=LOW, start_time="09:00"))

    scheduler = Scheduler.from_pet(pet)
    ordered = scheduler.sort_by_priority_then_time()

    # HIGH first (earliest-time HIGH before later HIGH), then MEDIUM, then LOW.
    assert [t.name for t in ordered] == [
        "Morning meds",  # HIGH 07:00
        "Evening meds",  # HIGH 20:00
        "Lunch play",    # MEDIUM 12:00
        "Brush",         # LOW 09:00
    ]
    # Priorities are non-decreasing across the whole ordering.
    priorities = [t.priority for t in ordered]
    assert priorities == sorted(priorities)


def test_scheduler_filters_by_pet_and_status():
    owner = Owner(name="Vanderwalls", available_time=120)
    roxa = Pet(name="Roxa", species="dog", age=4)
    garfield = Pet(name="Garfield", species="cat", age=2)
    roxa.add_task(Task(name="Walk", duration=30, priority=HIGH, start_time="08:00"))
    garfield.add_task(Task(name="Feed", duration=10, priority=HIGH, start_time="08:30"))
    garfield.get_tasks()[0].mark_complete()
    owner.add_pet(roxa)
    owner.add_pet(garfield)

    scheduler = Scheduler.from_owner(owner)

    roxa_tasks = scheduler.filter_tasks(pet_name="roxa")  # case-insensitive
    assert [t.name for t in roxa_tasks] == ["Walk"]

    done = scheduler.filter_tasks(completed=True)
    assert [t.name for t in done] == ["Feed"]


def test_conflict_detection_finds_same_start_time():
    pet = Pet(name="Roxa", species="dog", age=4)
    pet.add_task(Task(name="Walk", duration=30, priority=HIGH, start_time="08:00"))
    pet.add_task(Task(name="Feed", duration=10, priority=HIGH, start_time="08:00"))
    pet.add_task(Task(name="Play", duration=20, priority=LOW, start_time="12:00"))

    scheduler = Scheduler.from_pet(pet)
    conflicts = scheduler.find_conflicts()

    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_find_time_conflict_detects_exact_start_time():
    walk = Task(name="Walk", duration=30, priority=HIGH, start_time="08:00")
    play = Task(name="Play", duration=20, priority=LOW, start_time="12:00")
    existing = [walk, play]

    # A new task at an already-used time returns the clashing task.
    conflict = find_time_conflict(existing, "08:00")
    assert conflict is walk

    # A free time returns None.
    assert find_time_conflict(existing, "09:30") is None

    # No existing tasks means no conflict.
    assert find_time_conflict([], "08:00") is None


def test_recurring_task_creates_next_occurrence():
    scheduler = Scheduler()
    daily = Task(name="Walk", duration=30, priority=HIGH, start_time="08:00", frequency="daily")
    weekly = Task(name="Bath", duration=20, priority=LOW, start_time="10:00", frequency="weekly")
    one_time = Task(name="Vet visit", duration=45, priority=HIGH, frequency="one-time")

    next_daily = scheduler.next_occurrence(daily, from_date=date(2026, 7, 3))
    assert next_daily is not None
    assert next_daily[0] == date(2026, 7, 4)
    assert next_daily[1].name == "Walk"

    next_weekly = scheduler.next_occurrence(weekly, from_date=date(2026, 7, 3))
    assert next_weekly[0] == date(2026, 7, 10)

    assert scheduler.next_occurrence(one_time) is None


def test_completing_daily_task_returns_fresh_next_occurrence():
    scheduler = Scheduler()
    walk = Task(name="Walk", duration=30, priority=HIGH, start_time="08:00", frequency="daily")

    # Complete today's task, the way an owner would after their morning walk.
    walk.mark_complete()
    assert walk.completion_status is True

    result = scheduler.next_occurrence(walk, from_date=date(2026, 7, 3))
    assert result is not None
    next_date, next_task = result

    # Tomorrow's occurrence should be scheduled for the following day...
    assert next_date == date(2026, 7, 4)
    # ...and start over as NOT done, so it still gets scheduled tomorrow.
    assert next_task.completion_status is False