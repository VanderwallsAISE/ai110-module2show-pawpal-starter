import streamlit as st

# Connect the UI to the real backend logic in pawpal_system.py.
from pawpal_system import (
    Owner,
    Pet,
    Task,
    Scheduler,
    HIGH,
    MEDIUM,
    LOW,
    clean_name,
    is_valid_name,
    find_time_conflict,
)


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+, a pet care planning assistant. Add your pets, give each pet
some care tasks, then generate an explainable daily plan that fits your time budget.
"""
)

# Turn the UI priority words into the number constants the backend expects.
PRIORITY_OPTIONS = {"high": HIGH, "medium": MEDIUM, "low": LOW}

# Common species and preset task titles keep input friendly and consistent.
SPECIES_OPTIONS = [
    "dog", "cat", "bird", "rabbit", "fish",
    "hamster", "guinea pig", "turtle", "other",
]
TASK_PRESETS = [
    "Morning walk", "Feeding", "Medication", "Grooming",
    "Play / enrichment", "Clean litter box", "Vet appointment", "Other",
]
FREQUENCY_OPTIONS = ["one-time", "daily", "weekly"]

# --- Store ONE Owner object in session_state so the app remembers pets/tasks ---
# st.session_state survives button clicks, so the same Owner stays alive across
# reruns instead of being rebuilt (and wiped) every time the user clicks.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time=120)

owner = st.session_state.owner

st.divider()

# ------------------------------ Owner settings ------------------------------
st.subheader("Owner")

# Initialize the owner-name widget ONCE, then let its key drive the value.
if "owner_name_input" not in st.session_state:
    st.session_state.owner_name_input = owner.name

owner_name_value = st.text_input("Owner name", key="owner_name_input")

# Validate through the backend helper. Only write a clean, valid name back to
# the Owner object; invalid text (e.g. "Jordan3344") shows an error and the
# backend owner.name keeps its previous valid value.
if is_valid_name(owner_name_value):
    owner.name = clean_name(owner_name_value)
else:
    st.error("Owner name can only contain letters, spaces, hyphens, and apostrophes.")

# Fix the "two clicks" problem: initialize the widget's value in session_state
# ONCE, then let its key drive the value (do not also pass value=). Now a single
# click on plus/minus updates immediately, and we sync it back to the owner.
if "available_time_input" not in st.session_state:
    st.session_state.available_time_input = owner.available_time

st.number_input(
    "Available time today (minutes)",
    min_value=1,
    max_value=1440,
    step=5,
    key="available_time_input",
)
owner.available_time = st.session_state.available_time_input

# Simple reset: forget the saved owner AND every related widget key, then start
# fresh. This is the beginner-friendly alternative to a database or multiple
# accounts, and it also clears any invalid text left in the input widgets.
if st.button("Reset demo"):
    for key in (
        "owner",  # the saved Owner object (pets + tasks)
        "owner_name_input",
        "available_time_input",
        "pet_name_input",
        "species_input",
        "pet_age_input",
        "task_preset_input",
        "custom_task_input",
        "duration_input",
        "priority_input",
        "frequency_input",
        "start_time_input",
    ):
        st.session_state.pop(key, None)
    st.rerun()

st.divider()

# --------------------------------- Add a pet --------------------------------
st.subheader("Add a Pet")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
with col2:
    species = st.selectbox("Species", SPECIES_OPTIONS, key="species_input")
with col3:
    pet_age = st.number_input(
        "Age (years)", min_value=0, max_value=40, value=3, key="pet_age_input"
    )

if st.button("Add pet"):
    try:
        # Build a real Pet object and hand it to the Owner. Name validation
        # (letters, spaces, hyphens, apostrophes only) happens in the backend.
        new_pet = Pet(name=pet_name, species=species, age=int(pet_age))
        owner.add_pet(new_pet)
        st.success(f"Added pet '{new_pet.name}'.")
    except ValueError as error:
        # add_pet raises ValueError for empty/invalid names or duplicates.
        st.error(str(error))

# Show the pets the owner currently has.
if owner.get_pets():  # check if not empty (empty list = no pets yet)
    st.write("Current pets:")
    for pet in owner.get_pets():
        st.write(f"- {pet.name} ({pet.species}, age {pet.age}) — {len(pet.get_tasks())} task(s)")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# -------------------------------- Add a task --------------------------------
st.subheader("Add a Task")

if not owner.get_pets():  # check if no pets yet (empty list)
    st.info("Add a pet first, then you can give it tasks.")
else:
    # Let the user pick which pet receives the task.
    pet_names = [pet.name for pet in owner.get_pets()]
    chosen_pet_name = st.selectbox("Which pet gets this task?", pet_names)

    # Preset task titles keep input consistent; "Other" reveals a text box.
    preset_choice = st.selectbox("Task", TASK_PRESETS, key="task_preset_input")
    if preset_choice == "Other":
        task_title = st.text_input("Custom task title", value="", key="custom_task_input")
    else:
        task_title = preset_choice

    tcol1, tcol2, tcol3 = st.columns(3)
    with tcol1:
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20, key="duration_input"
        )
    with tcol2:
        priority_word = st.selectbox(
            "Priority", ["high", "medium", "low"], index=1, key="priority_input"
        )
    with tcol3:
        frequency = st.selectbox(
            "Frequency", FREQUENCY_OPTIONS, index=1, key="frequency_input"
        )

    start_time = st.time_input("Start time", key="start_time_input")

    if st.button("Add task"):
        try:
            # Find the Pet object the user chose.
            selected_pet = next(
                pet for pet in owner.get_pets() if pet.name == chosen_pet_name
            )
            # Map the priority word to a constant, then build a real Task.
            # start_time is stored as an "HH:MM" string the scheduler understands.
            new_task = Task(
                name=task_title,
                duration=int(duration),
                priority=PRIORITY_OPTIONS[priority_word],
                start_time=start_time.strftime("%H:%M"),
                frequency=frequency,
            )
            # Block exact-time conflicts BEFORE adding. Check across every pet so
            # two pets can't be booked for the same minute (O(n) helper).
            conflict = find_time_conflict(owner.get_all_tasks(), new_task.start_time)
            if conflict:
                st.error(
                    f"Time conflict at {conflict.start_time}: "
                    f"{conflict.pet_name}'s '{conflict.name}' is already scheduled then. "
                    "Pick a different start time."
                )
            else:
                selected_pet.add_task(new_task)  # validates the final title in the backend
                st.success(f"Added task '{new_task.name}' to {selected_pet.name}.")
        except ValueError as error:
            # add_task raises ValueError for invalid or duplicate tasks.
            st.error(str(error))

    # Show the tasks for each pet.
    for pet in owner.get_pets():
        tasks = pet.get_tasks()
        if tasks:
            st.write(f"**{pet.name}'s tasks:**")
            for task in tasks:
                st.write(
                    f"- {task.start_time} {task.name}: {task.duration} min "
                    f"(priority {task.priority}, {task.frequency})"
                )

st.divider()

# ----------------------------- Generate schedule ----------------------------
st.subheader("Build Schedule")
st.caption("Creates a plan of the highest-priority tasks that fit your time budget.")

if st.button("Generate schedule"):
    try:
        # Build the scheduler from every task across all of the owner's pets.
        scheduler = Scheduler.from_owner(owner)
        plan = scheduler.generate_daily_plan(owner)

        # Show conflict warnings without crashing (same-start-time tasks).
        for warning in scheduler.find_conflicts():
            st.warning(warning)

        # Table-style display that makes clear which pet each task belongs to.
        st.markdown("### Today's Plan")
        priority_labels = {HIGH: "high", MEDIUM: "medium", LOW: "low"}
        rows = [
            {
                "Time": task.start_time,
                "Pet": task.pet_name,
                "Task": task.name,
                "Duration (min)": task.duration,
                "Priority": priority_labels[task.priority],
            }
            for task in sorted(plan, key=lambda t: t.start_time)
        ]
        st.table(rows)
        total = sum(task.duration for task in plan)
        st.caption(f"Total: {total} min across {len(plan)} task(s).")
    except ValueError as error:
        # generate_daily_plan raises ValueError if there are no tasks / no time.
        st.error(str(error))
