"""PawPal+ demo.

A tiny, runnable example that builds an owner with two pets, gives each pet
some care tasks, then uses the Scheduler to print today's plan.
"""

from pawpal_system import Owner, Pet, Task, Scheduler, HIGH, MEDIUM, LOW


def main() -> None:
    # 1. Create one owner with a daily time budget (in minutes).
    owner = Owner(name="Vanderwalls", available_time=90)

    # 2. Create at least two pets.
    roxa = Pet(name="Roxa", species="dog", age=4)
    garfield = Pet(name="Garfield", species="cat", age=2)

    # 3. Add at least three tasks with different durations and priorities.
    roxa.add_task(Task(name="Morning walk", duration=30, priority=HIGH))
    roxa.add_task(Task(name="Brush coat", duration=15, priority=LOW))
    garfield.add_task(Task(name="Feed", duration=10, priority=HIGH))
    garfield.add_task(Task(name="Play with toys", duration=20, priority=MEDIUM))

    # 4. Add the pets to the owner.
    owner.add_pet(roxa)
    owner.add_pet(garfield)

    # 5. Build a scheduler from all of the owner's pets/tasks and plan the day.
    scheduler = Scheduler.from_owner(owner)
    scheduler.generate_daily_plan(owner)

    # 6. Print a clear, readable schedule.
    print("=" * 34)
    print("Today's Schedule for", owner.name)
    print("=" * 34)
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
