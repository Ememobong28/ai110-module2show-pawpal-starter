# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Testing PawPal+

Run the full test suite with:

```bash
python3 -m pytest
```

The suite covers 13 tests across five areas:

| Area | What is verified |
|---|---|
| Task completion | `mark_complete()` flips the status flag |
| Sorting | High priority scheduled before low; shorter task wins ties |
| Recurrence | Daily/weekly tasks auto-queue the next occurrence; `as-needed` tasks do not |
| Conflict detection | Overlapping start times produce a warning; touching (non-overlapping) times do not |
| Edge cases | Owner with 0 available minutes, pet with no tasks, unknown pet filter |

**Confidence level: ★★★★☆**
Core scheduling logic is well-covered. Lower confidence on the UI layer (Streamlit interactions are not tested) and on multi-day recurrence chains.

---

## Features

| Feature | Description |
|---|---|
| Multi-pet support | Add as many pets as you need; each owns its own task list |
| Priority scheduling | High-priority tasks are always planned first; shorter tasks win tiebreaks |
| Conflict detection | Tasks with overlapping fixed start times trigger a clear warning before the plan is shown |
| Recurring tasks | Daily and weekly tasks automatically queue the next occurrence when marked complete |
| Filtering | View tasks by pet or by completion status (pending / done) |
| Skipped task explanation | Any task that doesn't fit the available time window is listed with a reason |
| Progress bar | Visual indicator of how much of the day's available time the plan uses |

## 📸 Demo

_Add a screenshot of your running Streamlit app here using the embed syntax below:_

```html
<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank">
  <img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App'
       width='' alt='PawPal App' class='center-block' />
</a>
```

---

## Smarter Scheduling

PawPal+ goes beyond a simple task list with four algorithmic features:

- **Priority + duration sorting** — tasks are ordered by priority (high → low), with shorter tasks scheduled first when two tasks share the same priority. This packs more care into the available window.
- **Filtering** — tasks can be filtered by pet name or completion status, so the owner can ask "what has Buddy done today?" or "what is still pending?"
- **Recurring tasks** — tasks marked as `daily` or `weekly` automatically queue a new instance for the next due date when completed, so nothing falls off the radar.
- **Conflict detection** — if two tasks have fixed start times that overlap, the scheduler prints a warning before generating the plan. It warns rather than crashes, keeping the app usable even with bad input.

---

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
