
from dataclasses import dataclass
from drafter import *


@dataclass
class Assignment:
    """Save one homework assignment."""
    title: str
    class_name: str
    days_left: int
    minutes_needed: int
    done: bool


@dataclass
class State:
    """Save the student's work and choices."""
    assignments: list[Assignment]
    selected_class: str
    show_completed: bool
    total_study_minutes: int
    message: str


@route
def index(state: State) -> Page:
    """Show the home page."""
    return Page(state, [
        Header("Campus Study Planner"),
        Paragraph("Plan your homework and study time."),
        Paragraph(state.message),
        Paragraph("You have " + str(len(state.assignments)) + " assignments."),
        Link("Add homework", "add_page"),
        Link("My homework", "assignments_page"),
        Link("My progress", "progress_page"),
        Link("Study time", "study_page")
    ])


@route
def add_page(state: State) -> Page:
    """Show boxes to add homework."""
    return Page(state, [
        Header("Add Homework"),
        Paragraph(state.message),
        Paragraph("Homework name:"),
        TextBox("title"),
        Paragraph("Class name:"),
        TextBox("class_name"),
        Paragraph("Days until due (0 means today):"),
        TextBox("days_text", "2"),
        Paragraph("Minutes needed:"),
        TextBox("minutes_text", "30"),
        Button("Save Homework", "save_assignment")
    ])


@route
def save_assignment(state: State, title: str, class_name: str,
                    days_text: str, minutes_text: str) -> Page:
    """Add homework if the boxes have good values."""
    if title.strip() == "" or class_name.strip() == "":
        state.message = "Please type a homework name and class."
        return add_page(state)
    try:
        days = int(days_text)
        minutes = int(minutes_text)
    except ValueError:
        state.message = "Please use whole numbers for days and minutes."
        return add_page(state)
    if days < 0 or minutes <= 0:
        state.message = "Days must be 0 or more. Minutes must be above 0."
        return add_page(state)
    new_work = Assignment(title.strip(), class_name.strip(), days, minutes, False)
    state.assignments.append(new_work)
    state.message = "Homework added!"
    return assignments_page(state)


@route
def assignments_page(state: State) -> Page:
    """Show homework and let the student open each item."""
    items = [
        Header("My Homework"),
        Paragraph(state.message),
        Paragraph("Class: " + (state.selected_class or "All classes")),
        Link("Choose a class", "filter_page"),
        Button("Show or hide finished work", "toggle_completed_view"),
        Link("Add homework", "add_page"),
        Link("Home", "index")
    ]
    shown = 0
    for number in range(len(state.assignments)):
        work = state.assignments[number]
        if state.selected_class != "":
            if work.class_name.lower() != state.selected_class.lower():
                continue
        if work.done and not state.show_completed:
            continue
        status = "Done" if work.done else "Not done"
        items.append(Header(work.title))
        items.append(Paragraph("Class: " + work.class_name))
        if work.days_left <= 2 and not work.done:
            items.append(Paragraph("Due soon!"))
        items.append(Paragraph("Due in " + str(work.days_left) + " days"))
        items.append(Paragraph("Time: " + str(work.minutes_needed) + " minutes"))
        items.append(Paragraph("Status: " + status))
        items.append(Link("Open this homework", "assignment_details",
                          [Argument("number", number)]))
        shown = shown + 1
    if shown == 0:
        items.append(Paragraph("No homework to show."))
    return Page(state, items)


@route
def assignment_details(state: State, number: int) -> Page:
    """Show one homework item."""
    if number < 0 or number >= len(state.assignments):
        state.message = "Homework not found."
        return assignments_page(state)
    work = state.assignments[number]
    status = "Done" if work.done else "Not done"
    return Page(state, [
        Header(work.title),
        Paragraph("Class: " + work.class_name),
        Paragraph("Due in " + str(work.days_left) + " days"),
        Paragraph("Time needed: " + str(work.minutes_needed) + " minutes"),
        Paragraph("Status: " + status),
        Button("Change done status", "toggle_assignment", [Argument("number", number)]),
        Link("Back to homework", "assignments_page")
    ])


@route
def toggle_assignment(state: State, number: int) -> Page:
    """Change only the selected homework item."""
    if number < 0 or number >= len(state.assignments):
        state.message = "Homework not found."
        return assignments_page(state)
    work = state.assignments[number]
    work.done = not work.done
    state.message = "Homework updated."
    return assignment_details(state, number)


@route
def filter_page(state: State) -> Page:
    """Ask which class to show."""
    return Page(state, [
        Header("Choose a Class"),
        Paragraph("Type a class name or leave blank for all classes."),
        TextBox("class_filter", state.selected_class),
        Button("Save class choice", "set_class_filter")
    ])


@route
def set_class_filter(state: State, class_filter: str) -> Page:
    """Save the class choice."""
    state.selected_class = class_filter.strip()
    state.message = "Class choice saved."
    return assignments_page(state)


@route
def toggle_completed_view(state: State) -> Page:
    """Show or hide finished homework."""
    state.show_completed = not state.show_completed
    state.message = "Finished homework view changed."
    return assignments_page(state)


@route
def progress_page(state: State) -> Page:
    """Show work finished and time still needed."""
    done_count = 0
    minutes_left = 0
    for work in state.assignments:
        if work.done:
            done_count = done_count + 1
        else:
            minutes_left = minutes_left + work.minutes_needed
    return Page(state, [
        Header("My Progress"),
        Paragraph("Homework added: " + str(len(state.assignments))),
        Paragraph("Homework done: " + str(done_count)),
        Paragraph("Minutes of homework left: " + str(minutes_left)),
        Paragraph("Minutes studied: " + str(state.total_study_minutes)),
        Link("Add study time", "study_page"),
        Link("Home", "index")
    ])


@route
def study_page(state: State) -> Page:
    """Show a box to enter study time."""
    return Page(state, [
        Header("Study Time"),
        Paragraph("Minutes studied so far: " + str(state.total_study_minutes)),
        Paragraph(state.message),
        Paragraph("How many minutes did you study?"),
        TextBox("minutes_text", "20"),
        Button("Save study time", "log_study_minutes")
    ])


@route
def log_study_minutes(state: State, minutes_text: str) -> Page:
    """Add new study minutes to the total."""
    try:
        minutes = int(minutes_text)
    except ValueError:
        state.message = "Please enter a whole number."
        return study_page(state)
    if minutes <= 0:
        state.message = "Please enter more than 0 minutes."
        return study_page(state)
    state.total_study_minutes = state.total_study_minutes + minutes
    state.message = "Study time saved!"
    return progress_page(state)


set_website_title("Campus Study Planner")
set_site_information(
    author="Zuhaib",
    description="A simple study planner for schoolwork.",
    sources="CISC108 notes, Drafter docs, and ChatGPT",
    planning="Week 10 and Week 11 planning worksheets in this repository",
    links=[]
)
hide_debug_information()
start_server(State([], "", True, 0, ""))
