from datetime import date, timedelta
import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# ── existing tests (kept) ────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = Task(title="Morning walk", duration_minutes=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="cat")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Feed Mochi", duration_minutes=5, priority="high"))
    assert len(pet.tasks) == 1


# ── sorting ──────────────────────────────────────────────────────────────────

def test_scheduler_orders_high_before_low():
    """High-priority tasks must appear before low-priority ones in the plan."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(title="Playtime",  duration_minutes=10, priority="low"))
    pet.add_task(Task(title="Meds",      duration_minutes=10, priority="high"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).generate()
    titles = [t.title for t in schedule.planned_tasks]
    assert titles.index("Meds") < titles.index("Playtime")


def test_scheduler_breaks_priority_ties_by_shorter_duration():
    """When two tasks share a priority, the shorter one should be scheduled first."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(title="Long walk",   duration_minutes=30, priority="high"))
    pet.add_task(Task(title="Quick meds",  duration_minutes=5,  priority="high"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).generate()
    titles = [t.title for t in schedule.planned_tasks]
    assert titles.index("Quick meds") < titles.index("Long walk")


# ── recurrence ───────────────────────────────────────────────────────────────

def test_completing_daily_task_queues_next_occurrence():
    """Completing a daily task should add a new task due tomorrow."""
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(title="Feed Mochi", duration_minutes=5, priority="high", frequency="daily"))

    pet.complete_task("Feed Mochi")

    assert len(pet.tasks) == 2
    next_task = pet.tasks[-1]
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_completing_weekly_task_queues_seven_days_out():
    """Completing a weekly task should add a new task due in 7 days."""
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(title="Flea treatment", duration_minutes=10, priority="medium", frequency="weekly"))

    pet.complete_task("Flea treatment")

    next_task = pet.tasks[-1]
    assert next_task.due_date == date.today() + timedelta(weeks=1)


def test_as_needed_task_does_not_recur():
    """An 'as-needed' task should not create a follow-up when completed."""
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(title="Vet visit", duration_minutes=60, priority="high", frequency="as-needed"))

    pet.complete_task("Vet visit")

    assert len(pet.tasks) == 1   # no new task added


# ── conflict detection ───────────────────────────────────────────────────────

def test_overlapping_start_times_produce_warning():
    """Two tasks whose time windows overlap should trigger a conflict warning."""
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(title="Meds",  duration_minutes=20, priority="high", start_time="08:00"))
    pet.add_task(Task(title="Walk",  duration_minutes=30, priority="high", start_time="08:10"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts(owner.get_all_tasks())
    assert len(warnings) == 1
    assert "Meds" in warnings[0]
    assert "Walk" in warnings[0]


def test_touching_but_not_overlapping_times_are_clean():
    """A task that ends exactly when the next one starts is not a conflict."""
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(title="Meds",  duration_minutes=15, priority="high", start_time="08:00"))
    pet.add_task(Task(title="Walk",  duration_minutes=30, priority="high", start_time="08:15"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts(owner.get_all_tasks())
    assert warnings == []


# ── filtering ────────────────────────────────────────────────────────────────

def test_filter_by_status_separates_done_and_pending():
    """Completed and pending tasks should be returned in separate filtered lists."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="cat")
    done_task = Task(title="Feed Mochi", duration_minutes=5, priority="high")
    done_task.mark_complete()
    pet.add_task(done_task)
    pet.add_task(Task(title="Clean litter", duration_minutes=10, priority="medium"))
    owner.add_pet(pet)

    assert len(owner.filter_tasks_by_status(completed=True)) == 1
    assert len(owner.filter_tasks_by_status(completed=False)) == 1


def test_filter_by_pet_returns_empty_for_unknown_pet():
    """Filtering by a pet name that doesn't exist should return an empty list."""
    owner = Owner(name="Jordan", available_minutes=60)
    assert owner.filter_tasks_by_pet("Ghost") == []


# ── schedule generation edge cases ───────────────────────────────────────────

def test_zero_available_minutes_skips_all_tasks():
    """With no time available, every task should land in skipped_tasks."""
    owner = Owner(name="Jordan", available_minutes=0)
    pet = Pet(name="Buddy", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, priority="high"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).generate()
    assert schedule.planned_tasks == []
    assert len(schedule.skipped_tasks) == 1


def test_pet_with_no_tasks_produces_empty_schedule():
    """An owner whose pets have no tasks should get an empty plan."""
    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(Pet(name="Buddy", species="dog"))

    schedule = Scheduler(owner).generate()
    assert schedule.planned_tasks == []
    assert schedule.skipped_tasks == []
    assert schedule.total_duration == 0
