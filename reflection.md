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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
