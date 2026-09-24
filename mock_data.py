from models import Employee, SkillLevel, Task, TaskPriority, CalendarEvent, TaskExtraction, TaskStatus
from datetime import datetime, timedelta
import uuid
# Create the 10-person initial team
MOCK_EMPLOYEES = [
    Employee(employee_id="E01", name="Alice", role="Project Manager", skills={"Agile": SkillLevel.EXPERT, "Communication": SkillLevel.EXPERT}),
    Employee(employee_id="E02", name="Bob", role="Backend Developer", skills={"Python": SkillLevel.EXPERT, "FastAPI": SkillLevel.ADVANCED, "PostgreSQL": SkillLevel.INTERMEDIATE}),
    Employee(employee_id="E03", name="Charlie", role="Frontend Developer", skills={"React": SkillLevel.EXPERT, "TypeScript": SkillLevel.ADVANCED, "UI/UX": SkillLevel.BASIC}),
    Employee(employee_id="E04", name="Diana", role="AI/ML Engineer", skills={"Python": SkillLevel.EXPERT, "PyTorch": SkillLevel.ADVANCED, "LLMs": SkillLevel.EXPERT}),
    Employee(employee_id="E05", name="Eve", role="QA Engineer", skills={"Testing": SkillLevel.EXPERT, "Python": SkillLevel.INTERMEDIATE, "Automation": SkillLevel.ADVANCED}),
    Employee(employee_id="E06", name="Frank", role="DevOps Engineer", skills={"Docker": SkillLevel.EXPERT, "AWS": SkillLevel.ADVANCED, "CI/CD": SkillLevel.EXPERT}),
    Employee(employee_id="E07", name="Grace", role="UI/UX Designer", skills={"Figma": SkillLevel.EXPERT, "Design Systems": SkillLevel.ADVANCED}),
    Employee(employee_id="E08", name="Hank", role="Business Analyst", skills={"Requirements Gathering": SkillLevel.EXPERT, "SQL": SkillLevel.INTERMEDIATE}),
    Employee(employee_id="E09", name="Ivy", role="Data Engineer", skills={"SQL": SkillLevel.EXPERT, "Python": SkillLevel.ADVANCED, "Spark": SkillLevel.INTERMEDIATE}),
    Employee(employee_id="E10", name="Jack", role="Junior Developer", skills={"Python": SkillLevel.BASIC, "React": SkillLevel.BEGINNER, "Git": SkillLevel.BASIC}),
]

# Create some initial sample tasks
MOCK_TASKS = [
    Task(
        task_id="T101",
        title="Design Database Schema",
        description="Create the initial PostgreSQL schema for the workforce app.",
        project="AI Delivery Manager",
        priority=TaskPriority.HIGH,
        required_skills={"PostgreSQL": SkillLevel.INTERMEDIATE, "Python": SkillLevel.BASIC},
        estimated_effort_hours=6.0
    ),
    Task(
        task_id="T102",
        title="Develop Authentication API",
        description="Implement JWT based authentication in FastAPI.",
        project="AI Delivery Manager",
        priority=TaskPriority.CRITICAL,
        required_skills={"Python": SkillLevel.ADVANCED, "FastAPI": SkillLevel.ADVANCED},
        estimated_effort_hours=8.0,
        dependencies=["T101"] # Strict dependency on the database schema
    )
]

def get_all_employees() -> list[Employee]:
    return MOCK_EMPLOYEES

def get_all_tasks() -> list[Task]:
    return MOCK_TASKS

MOCK_TASKS[0].assigned_to = "E02"
MOCK_TASKS[0].status = "In Progress"

now = datetime.now()

MOCK_CALENDAR = [
    # Bob has a 2-hour architecture review tomorrow
    CalendarEvent(
        event_id="C01", employee_id="E02", title="Architecture Review",
        start_time=now + timedelta(days=1, hours=10), 
        end_time=now + timedelta(days=1, hours=12)
    ),
    # Bob has a 1-hour private appointment
    CalendarEvent(
        event_id="C02", employee_id="E02", title="Doctor Appointment",
        start_time=now + timedelta(days=2, hours=14), 
        end_time=now + timedelta(days=2, hours=15),
        is_private=True
    )
]

def get_employee_calendar(employee_id: str) -> list[CalendarEvent]:
    return [event for event in MOCK_CALENDAR if event.employee_id == employee_id]

def get_employee_active_tasks(employee_id: str) -> list[Task]:
    return [task for task in MOCK_TASKS if task.assigned_to == employee_id and task.status != "Done"]

def execute_task_assignment(task_req: TaskExtraction, assigned_employee_id: str) -> Task:
    """
    Takes the approved task requirements, generates a unique ID, 
    assigns it to the employee, and saves it to the database.
    """
    # Generate a random ID for the new task
    new_task_id = f"T-{str(uuid.uuid4())[:6].upper()}"
    
    new_task = Task(
        task_id=new_task_id,
        title=task_req.title,
        description=task_req.description,
        project="Ad-hoc Manager Request", # Defaulting for now
        priority=task_req.priority,
        required_skills=task_req.required_skills,
        estimated_effort_hours=task_req.estimated_effort_hours,
        status=TaskStatus.TODO,
        assigned_to=assigned_employee_id
    )
    
    # "Save" to our mock database
    MOCK_TASKS.append(new_task)
    
    return new_task

from models import HistoricalTaskLog

MOCK_HISTORY: list[HistoricalTaskLog] = [
    # Bob (E02) tends to finish backend tasks faster than estimated (factor ~0.85)
    HistoricalTaskLog(
        task_id="T090",
        employee_id="E02",
        task_type="Backend",
        estimated_hours=10.0,
        actual_hours=8.5,
        variance_ratio=0.85,
        completed_at=datetime.now() - timedelta(days=12)
    ),
    HistoricalTaskLog(
        task_id="T091",
        employee_id="E02",
        task_type="Backend",
        estimated_hours=20.0,
        actual_hours=17.0,
        variance_ratio=0.85,
        completed_at=datetime.now() - timedelta(days=5)
    ),
    # Jack (E10 - Junior) takes slightly longer as he learns (factor ~1.3)
    HistoricalTaskLog(
        task_id="T092",
        employee_id="E10",
        task_type="Backend",
        estimated_hours=8.0,
        actual_hours=10.5,
        variance_ratio=1.31,
        completed_at=datetime.now() - timedelta(days=8)
    )
]

def get_task_history() -> list[HistoricalTaskLog]:
    return MOCK_HISTORY