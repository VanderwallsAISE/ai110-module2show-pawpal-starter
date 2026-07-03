"""PawPal+ demo.

A tiny, runnable example that builds an owner with two pets, gives each pet
some care tasks, then uses the Scheduler to show off the Phase 4 algorithms:
sorting by time, filtering, conflict detection, recurring tasks, and the plan.
"""

from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler, HIGH, MEDIUM, LOW


def main() -> None:
    # 1. Create one owner with a daily time budget (in minutes).
    owner = Owner(name="Vanderwalls", available_time=90)

    # 2. Create at least two pets.
    roxa = Pet(name="Roxa", species="dog", age=4)
    garfield = Pet(name="Garfield", species="cat", age=2)

    # 3. Add tasks OUT OF ORDER by time, with mixed priorities, frequencies,
    #    statuses, and start times. Two tasks share 08:00 to show conflicts.
    roxa.add_task(Task(name="Brush coat", duration=15, priority=LOW,
                       start_time="18:00", frequency="weekly"))
    roxa.add_task(Task(name="Morning walk", duration=30, priority=HIGH,
                       start_time="08:00", frequency="daily"))
    garfield.add_task(Task(name="Feed", duration=10, priority=HIGH,
                           start_time="08:00", frequency="daily"))  # conflict w/ walk
    garfield.add_task(Task(name="Play with toys", duration=20, priority=MEDIUM,
                           start_time="12:00", frequency="one-time"))

    # Mark one task complete so filtering by status has something to show.
    garfield.get_tasks()[0].mark_complete()  # Feed is done

    # 4. Add the pets to the owner.
    owner.add_pet(roxa)
    owner.add_pet(garfield)

    # 5. Build a scheduler from all of the owner's pets/tasks.
    scheduler = Scheduler.from_owner(owner)

    # --- Sorted tasks by time -------------------------------------------------
    print("=" * 42)
    print("Tasks sorted by start time")
    print("=" * 42)
    for task in scheduler.sort_by_time():
        print(f"  {task.start_time}  {task.pet_name}: {task.name}")

    # --- Filtering ------------------------------------------------------------
    print("\n" + "=" * 42)
    print("Filtered tasks")
    print("=" * 42)
    print("Roxa's tasks:")
    for task in scheduler.filter_tasks(pet_name="Roxa"):
        print(f"  - {task.name}")
    print("Completed tasks:")
    for task in scheduler.filter_tasks(completed=True):
        print(f"  - {task.pet_name}: {task.name}")

    # --- Conflict detection ---------------------------------------------------
    print("\n" + "=" * 42)
    print("Conflict warnings")
    print("=" * 42)
    conflicts = scheduler.find_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  [!] {warning}")
    else:
        print("  No conflicts found.")

    # --- Recurring task example ----------------------------------------------
    print("\n" + "=" * 42)
    print("Recurring task example")
    print("=" * 42)
    walk = roxa.get_tasks()[1]  # Morning walk (daily)
    walk.mark_complete()
    result = scheduler.next_occurrence(walk, from_date=date(2026, 7, 3))
    if result:
        next_date, next_task = result
        print(f"  '{walk.name}' is {walk.frequency}; next occurrence on {next_date}"
              f" at {next_task.start_time}")

    # --- Today's generated schedule ------------------------------------------
    scheduler.generate_daily_plan(owner)
    print("\n" + "=" * 42)
    print("Today's Schedule for", owner.name)
    print("=" * 42)
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
