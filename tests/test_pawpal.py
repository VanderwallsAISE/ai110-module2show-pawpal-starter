from pawpal_system import Owner, Pet, Task, Scheduler, HIGH, MEDIUM, LOW


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