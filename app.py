import os
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Smart daily care planning for your pets.")

DATA_FILE = "data.json"

PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}
SPECIES_EMOJI  = {"dog": "🐶", "cat": "🐱", "other": "🐾"}

# --- Session state initialisation ---
# Load from data.json if it exists; otherwise start fresh.
if "owner" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.owner = Owner.load_from_json(DATA_FILE)
    else:
        st.session_state.owner = Owner(name="Jordan", available_minutes=60)


def save():
    """Persist current state to disk."""
    st.session_state.owner.save_to_json(DATA_FILE)


# ── Owner info ────────────────────────────────────────────────────────────────
st.subheader("Owner Info")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
with col2:
    available_minutes = st.number_input(
        "Available minutes today", min_value=0, max_value=480,
        value=st.session_state.owner.available_minutes
    )

if st.button("Update owner"):
    st.session_state.owner.name = owner_name
    st.session_state.owner.available_minutes = int(available_minutes)
    save()
    st.success(f"Updated: {owner_name}, {available_minutes} min available today.")

st.divider()

# ── Add a pet ─────────────────────────────────────────────────────────────────
st.subheader("Your Pets")
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    st.write("")
    st.write("")
    add_pet = st.button("Add pet")

if add_pet:
    existing_names = [p.name for p in st.session_state.owner.pets]
    if pet_name in existing_names:
        st.warning(f"**{pet_name}** is already in your list.")
    else:
        st.session_state.owner.add_pet(Pet(name=pet_name, species=species))
        save()
        st.success(f"Added {SPECIES_EMOJI.get(species, '🐾')} **{pet_name}** the {species}!")

if st.session_state.owner.pets:
    for pet in st.session_state.owner.pets:
        icon = SPECIES_EMOJI.get(pet.species, "🐾")
        pending = len(pet.pending_tasks())
        total = len(pet.tasks)
        st.markdown(f"- {icon} **{pet.name}** ({pet.species}) — {pending} pending / {total} total task(s)")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ── Add a task ────────────────────────────────────────────────────────────────
st.subheader("Add a Task")

if not st.session_state.owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    pet_names = [p.name for p in st.session_state.owner.pets]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        target_pet = st.selectbox("Assign to", pet_names)
    with col2:
        task_title = st.text_input("Task title", value="Morning walk")
    with col3:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col4:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col5, col6, col7 = st.columns(3)
    with col5:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"])
    with col6:
        start_time = st.text_input("Fixed start time (HH:MM)", value="", placeholder="optional")
    with col7:
        st.write("")
        st.write("")
        add_task = st.button("Add task")

    if add_task:
        pet = next(p for p in st.session_state.owner.pets if p.name == target_pet)
        pet.add_task(Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            start_time=start_time.strip() or None,
        ))
        save()
        st.success(f"{PRIORITY_EMOJI[priority]} Added **'{task_title}'** to {target_pet}.")

    # Task table with emoji priority column
    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.write("All tasks:")
        st.table([
            {
                "": PRIORITY_EMOJI.get(t.priority, ""),
                "pet": p.name,
                "task": t.title,
                "min": t.duration_minutes,
                "priority": t.priority,
                "frequency": t.frequency,
                "start": t.start_time or "—",
                "done": "✓" if t.completed else "",
            }
            for p in st.session_state.owner.pets
            for t in p.tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

    # Mark complete
    pending = st.session_state.owner.get_pending_tasks()
    if pending:
        st.write("Mark a task complete:")
        col1, col2 = st.columns([3, 1])
        with col1:
            task_to_complete = st.selectbox(
                "Select task",
                [f"{PRIORITY_EMOJI.get(t.priority, '')} {t.title}" for t in pending],
                label_visibility="collapsed"
            )
        with col2:
            if st.button("Mark done"):
                raw_title = task_to_complete.split(" ", 1)[-1]
                for pet in st.session_state.owner.pets:
                    titles = [t.title for t in pet.tasks]
                    if raw_title in titles:
                        pet.complete_task(raw_title)
                        break
                save()
                st.success(f"**'{raw_title}'** marked complete.")
                st.rerun()

st.divider()

# ── Generate schedule ─────────────────────────────────────────────────────────
st.subheader("Today's Schedule")

if st.button("Generate schedule", type="primary"):
    owner = st.session_state.owner

    if not owner.pets or not owner.get_pending_tasks():
        st.warning("Add at least one pet and one pending task before generating a schedule.")
    else:
        scheduler = Scheduler(owner)

        # Conflict check
        conflicts = scheduler.detect_conflicts(owner.get_pending_tasks())
        if conflicts:
            st.error("**⚠️ Time conflicts detected — review before your day starts:**")
            for w in conflicts:
                st.warning(w)

        schedule = scheduler.generate()
        time_used = schedule.total_duration
        time_available = owner.available_minutes
        pct = int((time_used / time_available) * 100) if time_available else 0

        st.success(f"Schedule ready — **{time_used} of {time_available} min** used ({pct}%).")
        st.progress(min(pct, 100))

        if schedule.planned_tasks:
            st.markdown("**Planned tasks** (weighted score: priority + overdue bonus + frequency):")
            st.table([
                {
                    "": PRIORITY_EMOJI.get(t.priority, ""),
                    "task": t.title,
                    "min": t.duration_minutes,
                    "priority": t.priority,
                    "score": round(t.weighted_score(), 1),
                    "start": t.start_time or "flexible",
                }
                for t in schedule.planned_tasks
            ])

        if schedule.skipped_tasks:
            st.warning(f"**{len(schedule.skipped_tasks)} task(s) skipped** — not enough time:")
            st.table([
                {
                    "": PRIORITY_EMOJI.get(t.priority, ""),
                    "task": t.title,
                    "min": t.duration_minutes,
                    "priority": t.priority,
                }
                for t in schedule.skipped_tasks
            ])

        with st.expander("View plain-text summary"):
            st.text(schedule.summary())
