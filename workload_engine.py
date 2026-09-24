from models import Employee, WorkloadSummary
from mock_data import get_employee_calendar, get_employee_active_tasks

def calculate_employee_capacity(employee: Employee, days: int = 5) -> WorkloadSummary:
    """
    Deterministically calculates an employee's capacity over a given day window.
    Formula: (Working Days * Hours/Day) - (Meeting Hours + Active Task Hours)
    """
    total_base_hours = days * employee.working_hours_per_day
    
    # 1. Sum up meeting hours
    events = get_employee_calendar(employee.employee_id)
    meeting_hours = 0.0
    for event in events:
        duration = event.end_time - event.start_time
        meeting_hours += duration.total_seconds() / 3600.0

    # 2. Sum up existing task effort
    tasks = get_employee_active_tasks(employee.employee_id)
    task_hours = 0.0
    for task in tasks:
        if task.estimated_effort_hours:
            task_hours += task.estimated_effort_hours

    # 3. Calculate remaining
    remaining = total_base_hours - (meeting_hours + task_hours)
    
    # Ensure capacity doesn't go below 0 (for display purposes)
    remaining = max(0.0, remaining)

    return WorkloadSummary(
        employee_id=employee.employee_id,
        window_days=days,
        total_base_hours=total_base_hours,
        meeting_hours=meeting_hours,
        active_task_hours=task_hours,
        remaining_capacity=remaining
    )