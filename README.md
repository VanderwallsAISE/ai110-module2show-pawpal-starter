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

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Running python main.py demonstrates the Phase 4 algorithms in the terminal:

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

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest
The PawPal+ backend is tested with pytest. The tests verify the core scheduling logic, including task completion, task addition, name validation, chronological sorting, filtering by pet/status, recurring task behavior, and exact-time conflict detection.

To run the test suite:

python -m pytest

Successful test output:
================================================================================================== test session starts ===================================================================================================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\istea\CodePath\ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 12 items                                                                                                                                                                                                        

tests\test_pawpal.py ............                                                                                                                                                                                   [100%]

=================================================================================================== 12 passed in 0.05s ===================================================================================================

I feel confident that the core backend logic works because the automated tests verify the most important scheduling behaviors. I am leaving one star open because the Streamlit UI still requires manual testing, especially for session state behavior and user input interactions.
```

Sample test output:

```
================================================================================================== test session starts  ===================================================================================================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\istea\CodePath\ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 10 items                                                                                                                                                                                                        

tests\test_pawpal.py ..........                                                                                                                                                                                     [100%]

=================================================================================================== 10 passed in 0.12s ===================================================================================================
```

## 📐 Smarter Scheduling

Phase 4 adds four algorithmic behaviors to the `Scheduler`, plus name validation
helpers (`clean_name`, `is_valid_name`, `compare_key`) in `pawpal_system.py`.

| Feature | Method(s) | Behavior | Complexity |
|---------|-----------|----------|------------|
| Task sorting | `Scheduler.sort_by_time()` | Returns tasks ordered by `start_time` (`"HH:MM"`), earliest first, using Python's `sorted()`. | Time `O(n log n)`, space `O(n)` |
| Filtering | `Scheduler.filter_tasks(pet_name=None, completed=None)` | Returns tasks matching an optional pet name (case-insensitive) and/or completion status. Both filters are optional and combine. | Time `O(n)`, space `O(n)` |
| Conflict handling | `Scheduler.find_conflicts()` | Groups tasks by `start_time` in a dictionary and returns a warning string for any exact same-time clash. Lightweight exact-time detection only (no overlap ranges yet). | Time `O(n)`, space `O(n)` |
| Recurring tasks | `Scheduler.next_occurrence(task, from_date=None)` | For a `"daily"` or `"weekly"` task, returns `(next_date, new_task)` using `timedelta`. Returns `None` for `"one-time"` tasks. | Time `O(1)`, space `O(1)` |

**Sorting** — `sort_by_time()` parses each `"HH:MM"` string into minutes and sorts
ascending, so the schedule reads top-to-bottom through the day.

**Filtering** — `filter_tasks()` walks the task list once. Pass `pet_name` to keep
one pet's tasks, `completed` (`True`/`False`) to split done vs. pending, or both.

**Conflict detection** — `find_conflicts()` warns when two tasks share the exact
same `start_time`. The Streamlit UI shows these as non-blocking warnings so the
app never crashes on a clash.

**Recurring tasks** — when a `daily`/`weekly` task is marked complete,
`next_occurrence()` builds the next dated copy with `timedelta(days=1)` or
`timedelta(weeks=1)`.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
