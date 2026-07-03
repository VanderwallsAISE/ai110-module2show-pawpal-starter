# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the AI assistant (Claude Code) to implement two optional extensions while
keeping the scope controlled — no data persistence, database, login, or payment
features:

- **Challenge 3 — Advanced Priority Scheduling:** make scheduling sort by priority
  first (HIGH → MEDIUM → LOW), then by `start_time` on ties, and document the time
  and space complexity.
- **Challenge 4 — Professional UI and Output Formatting:** add priority indicators
  (🔴 High / 🟡 Medium / 🟢 Low) and task emojis (🍽️ Feeding, 🦮 Morning walk,
  💊 Medication, 🧼 Grooming, 🎾 Play / enrichment, 🧹 Clean litter box,
  🏥 Vet appointment) in the CLI and Streamlit output, without adding new
  libraries.

**Which files were modified?**

- `pawpal_system.py` — added `Scheduler.sort_by_priority_then_time()`, updated
  `generate_daily_plan()` to build the plan from that ordering, and added the
  `priority_label()` / `task_emoji()` helpers with the `PRIORITY_LABELS` and
  `TASK_EMOJIS` maps.
- `main.py` — added a "Tasks by priority, then start time" demo section, used the
  emoji/priority indicators, and added a `sys.stdout.reconfigure("utf-8")` call.
- `app.py` — the per-pet task tables and the *Today's Plan* table now use the
  indicators, and the plan is ordered with `sort_by_priority_then_time()`.
- `tests/test_pawpal.py` — added `test_scheduler_sorts_by_priority_then_time`.
- `README.md` — added an "Optional Extensions" section, a priority-based CLI output
  example, and updated the test count (12 → 13).
- `ai_interactions.md` — this log.

**What did the agent do / complete?**

- Implemented both challenges in a single pass and kept scheduling logic Pythonic
  (one `sorted()` call on the tuple key `(priority, start_time)`).
- Ran `python -m pytest` (13 passing) and `python main.py` to confirm the output,
  and compiled the files with `py_compile`.
- Documented the `O(n log n)` time / `O(n)` space complexity in the code, the
  README, and the summary.

**What did you have to verify or fix manually?**

- The agent first tried printing emojis directly and discovered the Windows
  console uses cp1252, which crashed with a `UnicodeEncodeError`. It verified the
  fix (`sys.stdout.reconfigure(encoding="utf-8")`) before committing to it —
  standard library only, no new dependency.
- The original demo task names in `main.py` (e.g. "Feed", "Brush coat") did not
  match the emoji keys, so they showed the fallback 🐾. I had it rename them to the
  recognized preset titles ("Feeding", "Grooming", "Play / enrichment") so the CLI
  demo actually showcases the emoji indicators.
- I still need to manually check the Streamlit UI in the browser, since the tables
  and session-state behavior are not covered by automated tests.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
