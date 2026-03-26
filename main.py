from pawpal_system import Task, Pet, Owner, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=60)

mochi = Pet(name="Mochi", species="cat")
buddy = Pet(name="Buddy", species="dog")

# --- Tasks for Mochi ---
mochi.add_task(Task(title="Feed Mochi", duration_minutes=5, priority="high"))
mochi.add_task(Task(title="Clean litter box", duration_minutes=10, priority="medium"))

# --- Tasks for Buddy ---
buddy.add_task(Task(title="Morning walk", duration_minutes=30, priority="high"))
buddy.add_task(Task(title="Give flea medication", duration_minutes=5, priority="high"))
buddy.add_task(Task(title="Enrichment / playtime", duration_minutes=20, priority="low"))

owner.add_pet(mochi)
owner.add_pet(buddy)

# --- Generate schedule ---
scheduler = Scheduler(owner)
schedule = scheduler.generate()

# --- Print today's schedule ---
print("=" * 40)
print(f"  Today's Schedule for {owner.name}")
print(f"  Available time: {owner.available_minutes} min")
print("=" * 40)

if schedule.planned_tasks:
    print("\nPlanned tasks:")
    for i, task in enumerate(schedule.planned_tasks, start=1):
        print(f"  {i}. {task.title:<25} {task.duration_minutes:>3} min  [{task.priority}]")
    print(f"\n  Total time used: {schedule.total_duration} min")

if schedule.skipped_tasks:
    print("\nSkipped (not enough time):")
    for task in schedule.skipped_tasks:
        print(f"  - {task.title:<25} {task.duration_minutes:>3} min  [{task.priority}]")

print("=" * 40)
