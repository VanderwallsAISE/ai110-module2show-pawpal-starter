# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design uses four main classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

The `Owner` class stores basic owner information, including the owner’s name, available time, preferences, and pets.

 The `Pet` class stores information about each pet, including the pet’s name, species, age, and care tasks. 

 The `Task` class represents one pet-care activity, such as walking, feeding, medication, grooming, or enrichment, and stores the task name, duration, priority, and category. 

 The `Scheduler` class is responsible for organizing tasks into a daily plan based on priority and the owner’s available time.

The main relationships are that one owner can have many pets, one pet can have many tasks, and the scheduler uses tasks to generate a daily care plan.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

During the design process, I changed where `available_time` belongs. At first, I considered putting `available_time` inside both `Owner` and `Scheduler`, but that created duplicated responsibility. I moved `available_time` fully to the `Owner` class because the owner is the person who knows how much time they have available. The `Scheduler` now uses the owner’s available time when generating the daily plan.

I also changed `preferences` from a simple string into a dictionary so the app can store multiple owner preferences in a cleaner way. This makes the design more flexible while still keeping the project simple.


### My initial design focuses on three core user actions:

 1. Add and manage owner and pet information so the system can store basic details about the owner, their preferences, and their pet.

 2. Create and edit pet care tasks such as feeding, walking, medication, grooming, and enrichment activities.

 3. Generate a daily schedule that prioritizes tasks based on importance, duration, available time, and owner preferences.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers two main constraints: the owner's **available time** (a
total number of minutes for the day) and each task's **priority** (high, medium,
or low). When it builds the daily plan, it sorts tasks by priority and then
greedily keeps each task whose duration still fits in the remaining time. It also
skips tasks that are already marked complete, since there is no reason to schedule
something that is already done.

I decided that time and priority mattered most because those are the two things a
busy owner actually feels: they only have so many minutes, and some tasks (like
medication) matter more than others (like an optional grooming session).
Preferences exist on the `Owner` as a dictionary so the design can grow, but I
kept the core scheduling logic focused on time and priority to stay
beginner-friendly and easy to test.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff my scheduler makes is that `generate_daily_plan()` is **greedy**
rather than optimal. It walks the priority-sorted list once and keeps whatever
fits, so it is simple and fast (`O(n log n)`), but it will not always pack the
absolute maximum number of tasks into the time budget the way a more complex
knapsack-style algorithm would. For a daily pet-care planner this is reasonable:
owners care more about doing the important things first than about squeezing in
the mathematically optimal set, and the greedy approach is much easier to read,
test, and reason about.

The scheduler currently uses lightweight **exact-time conflict detection**. The
`Scheduler.find_conflicts()` method warns when two tasks share the same
`start_time` (for example, two tasks both at 8:00), but it does **not** yet
detect full overlapping time ranges — it would miss an 8:00–8:30 task
overlapping an 8:15–8:45 task, because it only compares start times, not the
duration windows around them.

This tradeoff is reasonable for a beginner-friendly project: exact-time matching
is easy to read (a single dictionary grouping tasks by start time, `O(n)`) and
still clearly demonstrates conflict detection. Full interval-overlap checking
would mean sorting by start time and comparing each task's end time against the
next task's start time, which adds noticeably more logic for a scenario where
most clashes people care about happen at the same scheduled minute. If the app
grew into a real calendar, upgrading to interval-overlap detection would be the
natural next step.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI across every phase of the project, but I stayed in charge of the
decisions:

- **Brainstorming** — I used AI to talk through my four-class design (Owner, Pet,
  Task, Scheduler) and to sanity-check the relationships before I committed to
  them in UML.
- **Coding** — Once I knew the design, AI helped me turn the UML into Python class
  stubs and then fill in the scheduling methods incrementally.
- **Debugging** — When the Streamlit inputs needed two clicks to update, AI helped
  me understand that the fix was to initialize each widget's value in
  `session_state` once and let the key drive it instead of also passing `value=`.
- **Refactoring** — AI helped me pull name-cleaning and validation into small
  helper functions (`clean_name`, `compare_key`, `is_valid_name`) so the same
  rules are reused by Owner, Pet, and Task instead of being copy-pasted.
- **Documentation** — AI helped me organize the README into a project manual and
  write the algorithm complexity table.
- **Testing** — AI helped me brainstorm which behaviors were worth testing (sorting,
  filtering, conflicts, recurring tasks, time-budget limits) so my 12 pytest cases
  cover the important logic instead of trivial getters.

The most helpful prompts were specific and scoped, like "explain why this
Streamlit input needs two clicks" or "what edge cases should I test for
`next_occurrence`," rather than vague "write my project" prompts.

One thing that really helped organize the work was using **separate chat sessions
for each phase** (design, core logic, algorithms, testing, UI, and this final
polish phase). Keeping each phase in its own session meant the context stayed
focused — the testing session was about tests, the UI session was about
Streamlit — so I did not get confused by earlier decisions bleeding into unrelated
work, and it was easier to review one phase at a time.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

At one point AI suggested upgrading conflict detection to full
**overlapping-interval** checking (comparing each task's end time against the next
task's start time). It was a reasonable idea, but I **modified/rejected** it for
this project because it added noticeably more logic and edge cases for a
beginner-friendly app, and most clashes owners actually notice happen at the exact
same scheduled minute. I kept the simpler exact-time detection and instead wrote
down interval-overlap as the clear "next step" in this reflection. This kept the
design clean and honest about its limits.

I verified AI suggestions in two ways: I ran `python -m pytest` after backend
changes to make sure nothing broke, and I ran the app with `streamlit run app.py`
(and `python main.py` for the CLI) to confirm the behavior actually matched what
the AI described. When AI explained *why* something worked, I checked that the
explanation matched what I saw on screen before trusting it.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote 12 pytest cases covering the behaviors that make PawPal+ actually useful:
task completion, adding tasks to a pet, the scheduler only adding tasks that fit
the available time, name cleaning and validation, rejecting invalid pet names,
sorting by time, filtering by pet and status, exact-time conflict detection, the
`find_time_conflict` helper the UI uses to block clashes, and recurring
`next_occurrence` behavior (including that a completed daily task's next
occurrence resets to not-done).

These tests were important because they cover the logic a user depends on and the
places where a bug would be easy to miss by eye — for example, the time-budget cut
off and the recurring-task reset. Testing them means I can refactor with
confidence.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am fairly confident (about 4 out of 5) that the scheduler works correctly,
because the automated tests pass and cover the core behaviors. The star I hold
back is for the Streamlit UI, which I tested manually rather than automatically —
especially session-state behavior across button clicks.

If I had more time, I would test more edge cases: a task whose duration is exactly
equal to the remaining time, ties in priority (to confirm stable ordering keeps
the original order), invalid `start_time` strings, and a fuller
overlapping-interval version of conflict detection.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with how clean the four-class design stayed from UML all the
way to the final code. Because I designed it first, the classes have clear
responsibilities (Owner has pets, Pet has tasks, Scheduler does the planning), and
the scheduling helpers are small enough to read and test individually. I am also
happy that the exact-time conflict blocking works both when adding a task and as a
safety-net warning when generating the plan.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration, I would upgrade conflict detection to full
overlapping-interval checking so it catches an 8:00–8:30 task overlapping an
8:15–8:45 task, not just exact same-minute clashes. I would also add automated
tests for the Streamlit UI and let the owner edit or reorder tasks after adding
them, instead of only adding and removing.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The biggest thing I learned is what it feels like to be the **lead architect while
using AI tools**. AI is great at generating options and explaining tradeoffs, but
it does not know what my project should be — I do. My job was to hold the vision
(keep it beginner-friendly, four classes, aligned with CodePath), design the
structure first, and then use AI to move faster inside that structure while
verifying everything with tests and by running the app. When I stayed in the
architect role and treated AI as a collaborator instead of an autopilot, the
design stayed clean and I actually understood every part of my own project.
