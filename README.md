# 🐾 PawPal+

**PawPal+** is a Streamlit app that helps a busy pet owner plan daily care tasks
for their pets. You enter your pets and their care tasks (walks, feeding, meds,
grooming, enrichment), and PawPal+ builds an explainable daily plan that fits the
time you actually have — prioritizing what matters most and warning you about
scheduling clashes.

This project was built for CodePath Module 2. It was designed UML-first, then
implemented in plain Python (four classes only), tested with pytest, and wired to
a Streamlit UI.

---

## ✨ Features

- **Pet & task management** — Add multiple pets to one owner, and give each pet
  its own care tasks. Names are validated (letters, spaces, hyphens, apostrophes)
  and duplicate pets/tasks are rejected so the data stays clean.
- **Task details** — Every task carries a title, duration (minutes), priority
  (high / medium / low), start time, frequency, and completion status.
- **Sorting by time** — `Scheduler.sort_by_time()` orders tasks chronologically
  so the daily plan reads top-to-bottom through the day.
- **Filtering by pet / status** — `Scheduler.filter_tasks()` returns just one
  pet's tasks, only completed (or only pending) tasks, or any combination.
- **Recurring daily / weekly tasks** — `Scheduler.next_occurrence()` computes the
  next date for a `daily` or `weekly` task using `timedelta`, so a finished task
  reappears fresh (and not-done) on its next day.
- **Priority-based daily planning** — `Scheduler.generate_daily_plan()` greedily
  fills the owner's available minutes with the highest-priority tasks that fit.
- **Exact-time conflict detection & blocking** — `Scheduler.find_conflicts()`
  warns when two tasks share the exact same start time. In the UI, exact-time
  clashes are also **blocked before a task is added** so two tasks can't be booked
  for the same minute in the first place.
- **Streamlit UI** — A clean, single-page app for entering owners, pets, and
  tasks and generating the plan, with `st.success` / `st.error` / `st.warning`
  feedback and `st.table` schedule displays.
- **pytest test coverage** — 12 automated tests cover the core scheduling
  behaviors (see [Testing PawPal+](#-testing-pawpal)).

---

## 🚀 Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the CLI demo

```bash
python main.py
```

---

## 📸 Demo Walkthrough

The whole app lives on one page. Here is what you can do and a typical workflow.

**What you can do in the UI**

- Set the **owner's name** and **available time** (total minutes for the day).
- **Add pets** (name, species, age). Pets appear in a list with a task count.
- **Add tasks** to a chosen pet: pick a preset (or type a custom title), then set
  duration, priority, frequency, and start time.
- **Generate a schedule** that fits the owner's time budget and see it as a table.

**Example workflow: add owner → add pet → add task → generate schedule**

1. **Owner** — In the *Owner* section, set the name (e.g. `Jordan`) and available
   time (e.g. `120` minutes). Invalid names show an `st.error` and the previous
   valid name is kept.
2. **Add a pet** — In *Add a Pet*, enter `Mochi`, pick `cat`, age `3`, and click
   **Add pet**. A green `st.success` confirms it; duplicates or bad names show an
   `st.error`.
3. **Add tasks** — In *Add a Task*, choose the pet, pick a task (e.g. `Feeding`),
   set duration/priority/frequency/start time, and click **Add task**. Each pet's
   tasks show in a table (task, start time, duration, priority, frequency).
4. **Generate schedule** — Click **Generate schedule**. PawPal+ builds the plan
   and shows *Today's Plan* as a table with **pet name, task, start time,
   duration, priority, and frequency**, plus a summary of minutes used.

**Key scheduler behaviors shown**

- The plan only includes tasks whose durations fit the owner's available minutes,
  chosen highest-priority-first.
- The plan table is sorted chronologically by start time via `sort_by_time()`.
- Completed tasks are skipped when generating today's plan.

**Conflict handling**

- When adding a task, if another task (for *any* pet) already starts at that exact
  minute, PawPal+ **blocks the add** and shows an `st.error` explaining the clash,
  so you pick a different start time.
- When generating the schedule, `find_conflicts()` runs as a safety net and shows
  any exact same-time clashes as non-blocking `st.warning` messages — the app
  never crashes on a clash. If there are none, you get a green "No time conflicts
  detected." message.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

---

## 🖥️ Sample Output

Running `python main.py` demonstrates the scheduling algorithms in the terminal:

```
==========================================
Tasks sorted by start time
==========================================
  08:00  Roxa: Morning walk
  08:00  Garfield: Feed
  12:00  Garfield: Play with toys
  18:00  Roxa: Brush coat

==========================================
Filtered tasks
==========================================
Roxa's tasks:
  - Brush coat
  - Morning walk
Completed tasks:
  - Garfield: Feed

==========================================
Conflict warnings
==========================================
  [!] Conflict at 08:00: Roxa's Morning walk, Garfield's Feed

==========================================
Recurring task example
==========================================
  'Morning walk' is daily; next occurrence on 2026-07-04 at 08:00

==========================================
Today's Schedule for Vanderwalls
==========================================
- 12:00 | Garfield | Play with toys: 20 min (medium priority)
- 18:00 | Roxa | Brush coat: 15 min (low priority)
Total: 35 min across 2 task(s).
```

---

## 🧪 Testing PawPal+

The PawPal+ backend is tested with pytest. Run the full suite with:

```bash
python -m pytest
```

**What the tests cover**

- Task completion changing status
- Adding a task to a pet increases its task count
- The scheduler only adds tasks that fit the owner's available time
- `clean_name` collapses spaces and keeps capitalization
- Name validation accepts real names and rejects numbers/junk
- `add_pet` rejects invalid names
- Chronological sorting by start time (`sort_by_time`)
- Filtering by pet and by completion status (`filter_tasks`)
- Exact-time conflict detection (`find_conflicts`)
- The `find_time_conflict` helper used to block clashes in the UI
- Recurring daily/weekly `next_occurrence`, and that a completed daily task's next
  occurrence resets to not-done

**Sample passing output**

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\istea\CodePath\ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 12 items

tests\test_pawpal.py ............                                        [100%]

============================= 12 passed in 0.04s ==============================
```

**Confidence: ★★★★☆ (4 / 5)**

I feel confident the core backend logic works because the automated tests verify
the most important scheduling behaviors. I am leaving one star open because the
Streamlit UI still relies on manual testing, especially session-state behavior
and user input interactions.

---

## 📐 Smarter Scheduling (Algorithms)

The scheduling behaviors live in the `Scheduler`, plus name-validation helpers
(`clean_name`, `is_valid_name`, `compare_key`) in `pawpal_system.py`.

| Feature | Method(s) | Behavior | Complexity |
|---------|-----------|----------|------------|
| Task sorting | `Scheduler.sort_by_time()` | Returns tasks ordered by `start_time` (`"HH:MM"`), earliest first, using Python's `sorted()`. | Time `O(n log n)`, space `O(n)` |
| Filtering | `Scheduler.filter_tasks(pet_name=None, completed=None)` | Returns tasks matching an optional pet name (case-insensitive) and/or completion status. Both filters are optional and combine. | Time `O(n)`, space `O(n)` |
| Conflict handling | `Scheduler.find_conflicts()` | Groups tasks by `start_time` in a dictionary and returns a warning string for any exact same-time clash. Exact-time detection only (no overlap ranges yet). | Time `O(n)`, space `O(n)` |
| Recurring tasks | `Scheduler.next_occurrence(task, from_date=None)` | For a `"daily"` or `"weekly"` task, returns `(next_date, new_task)` using `timedelta`. Returns `None` for `"one-time"` tasks. | Time `O(1)`, space `O(1)` |
| Daily planning | `Scheduler.generate_daily_plan(owner)` | Greedily keeps the highest-priority tasks that still fit the owner's remaining time. | Time `O(n log n)`, space `O(n)` |

**Sorting** — `sort_by_time()` parses each `"HH:MM"` string into minutes and sorts
ascending, so the schedule reads top-to-bottom through the day.

**Filtering** — `filter_tasks()` walks the task list once. Pass `pet_name` to keep
one pet's tasks, `completed` (`True`/`False`) to split done vs. pending, or both.

**Conflict detection** — `find_conflicts()` warns when two tasks share the exact
same `start_time`. In the UI these are non-blocking warnings, while the
`find_time_conflict` helper blocks new exact-time clashes before they are added.

**Recurring tasks** — when a `daily`/`weekly` task is marked complete,
`next_occurrence()` builds the next dated copy with `timedelta(days=1)` or
`timedelta(weeks=1)`.

---

## 🗂️ Project Structure

```
pawpal_system.py      # Core domain model: Owner, Pet, Task, Scheduler + helpers
app.py                # Streamlit UI
main.py               # CLI demo of the scheduling algorithms
tests/test_pawpal.py  # pytest suite (12 tests)
diagrams/uml.mmd      # Original UML design
diagrams/uml_final.mmd# Final UML matching the implementation
reflection.md         # Design + AI-collaboration reflection
```
