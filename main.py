from tabulate import tabulate
from pawpal_system import Task, Pet, Owner, Scheduler

PRIORITY_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢"}
SPECIES_ICON  = {"dog": "🐶", "cat": "🐱", "other": "🐾"}

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=60)

mochi = Pet(name="Mochi", species="cat")
buddy = Pet(name="Buddy", species="dog")

# Tasks added out of order to verify sorting
mochi.add_task(Task(title="Clean litter box", duration_minutes=10, priority="medium"))
mochi.add_task(Task(title="Feed Mochi",       duration_minutes=5,  priority="high", frequency="daily"))

buddy.add_task(Task(title="Enrichment / playtime", duration_minutes=20, priority="low"))
buddy.add_task(Task(title="Give flea medication",  duration_minutes=20, priority="high",
                    start_time="08:00"))
buddy.add_task(Task(title="Morning walk",          duration_minutes=30, priority="high",
                    start_time="08:10"))   # overlaps with flea med

owner.add_pet(mochi)
owner.add_pet(buddy)

# ── Recurring task demo ────────────────────────────────────────────────────────
print("\n" + "━" * 52)
print("  RECURRING TASK DEMO")
print("━" * 52)
print(f"  Mochi tasks before completion : {len(mochi.tasks)}")
mochi.complete_task("Feed Mochi")
print(f"  Mochi tasks after  completion : {len(mochi.tasks)}")
next_task = mochi.tasks[-1]
print(f"  Next occurrence queued        : '{next_task.title}' due {next_task.due_date}")

# ── Schedule (with conflict check) ────────────────────────────────────────────
print("\n" + "━" * 52)
print(f"  Today's Schedule — {owner.name}")
print(f"  Available time    : {owner.available_minutes} min")
print("━" * 52)

scheduler = Scheduler(owner)
schedule  = scheduler.generate()

if schedule.planned_tasks:
    rows = [
        [
            PRIORITY_ICON.get(t.priority, ""),
            t.title,
            f"{t.duration_minutes} min",
            t.priority,
            f"{t.weighted_score():.0f}",
            t.start_time or "flexible",
        ]
        for t in schedule.planned_tasks
    ]
    print("\n" + tabulate(
        rows,
        headers=["", "Task", "Duration", "Priority", "Score", "Start"],
        tablefmt="rounded_outline",
    ))
    time_used = schedule.total_duration
    bar_filled = int((time_used / owner.available_minutes) * 30)
    bar = "█" * bar_filled + "░" * (30 - bar_filled)
    print(f"\n  [{bar}] {time_used}/{owner.available_minutes} min used\n")

if schedule.skipped_tasks:
    skipped_rows = [
        [PRIORITY_ICON.get(t.priority, ""), t.title, f"{t.duration_minutes} min", t.priority]
        for t in schedule.skipped_tasks
    ]
    print(tabulate(
        skipped_rows,
        headers=["", "Skipped Task", "Duration", "Priority"],
        tablefmt="rounded_outline",
    ))
    print()

# ── Filter: all pets summary ───────────────────────────────────────────────────
print("━" * 52)
print("  All Pets Summary")
print("━" * 52)
pet_rows = [
    [
        SPECIES_ICON.get(p.species, "🐾"),
        p.name,
        p.species,
        len(p.pending_tasks()),
        len(p.tasks),
    ]
    for p in owner.pets
]
print("\n" + tabulate(
    pet_rows,
    headers=["", "Pet", "Species", "Pending", "Total Tasks"],
    tablefmt="rounded_outline",
))

# ── Filter: completed tasks ────────────────────────────────────────────────────
print("\n" + "━" * 52)
print("  Completed Tasks Today")
print("━" * 52)
completed = owner.filter_tasks_by_status(completed=True)
if completed:
    print("\n" + tabulate(
        [["✓", t.title, t.priority] for t in completed],
        headers=["", "Task", "Priority"],
        tablefmt="rounded_outline",
    ))
else:
    print("  None completed yet.")

print()
