from pawpal_system import Task, Pet, Owner, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=60)

mochi = Pet(name="Mochi", species="cat")
buddy = Pet(name="Buddy", species="dog")

# Tasks added out of order to verify sorting
mochi.add_task(Task(title="Clean litter box", duration_minutes=10, priority="medium"))
mochi.add_task(Task(title="Feed Mochi",       duration_minutes=5,  priority="high", frequency="daily"))

buddy.add_task(Task(title="Enrichment / playtime", duration_minutes=20, priority="low"))
buddy.add_task(Task(title="Give flea medication",  duration_minutes=20, priority="high",
                    start_time="08:00"))   # runs 08:00–08:20
buddy.add_task(Task(title="Morning walk",          duration_minutes=30, priority="high",
                    start_time="08:10"))   # starts 08:10 → overlaps with flea med

owner.add_pet(mochi)
owner.add_pet(buddy)

# --- Recurring task demo ---
print("=" * 50)
print("  RECURRING TASK DEMO")
print("=" * 50)
print(f"  Mochi tasks before completion: {len(mochi.tasks)}")
mochi.complete_task("Feed Mochi")
print(f"  Mochi tasks after completion:  {len(mochi.tasks)}")
next_task = mochi.tasks[-1]
print(f"  New task queued: '{next_task.title}' due {next_task.due_date}")

# --- Conflict detection + schedule ---
print()
print("=" * 50)
print(f"  Today's Schedule for {owner.name}")
print(f"  Available time: {owner.available_minutes} min")
print("=" * 50)

scheduler = Scheduler(owner)
schedule = scheduler.generate()

if schedule.planned_tasks:
    print("\nPlanned tasks (priority desc, shortest first on ties):")
    for i, task in enumerate(schedule.planned_tasks, start=1):
        slot = f" @ {task.start_time}" if task.start_time else ""
        print(f"  {i}. {task.title:<28} {task.duration_minutes:>3} min  [{task.priority}]{slot}")
    print(f"\n  Total time used: {schedule.total_duration} min")

if schedule.skipped_tasks:
    print("\nSkipped (not enough time):")
    for task in schedule.skipped_tasks:
        print(f"  - {task.title:<28} {task.duration_minutes:>3} min  [{task.priority}]")

# --- Filter demos ---
print()
print("=" * 50)
print("  Filter: Buddy's tasks only")
print("=" * 50)
for t in owner.filter_tasks_by_pet("Buddy"):
    print(f"  - {t.title}")

print()
print("=" * 50)
print("  Filter: completed tasks")
print("=" * 50)
for t in owner.filter_tasks_by_status(completed=True):
    print(f"  - {t.title}")

print("=" * 50)
