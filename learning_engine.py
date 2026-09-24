from typing import List, Optional
from datetime import datetime
from models import HistoricalTaskLog, TaskCompletionRecord
from mock_data import get_task_history, get_all_tasks

def get_employee_calibration_factor(employee_id: str, task_type: str = "General") -> float:
    """
    Calculates the statistical variance ratio (actual / estimated) for an employee.
    A factor < 1.0 means the employee completes tasks faster than estimated.
    A factor > 1.0 means the employee requires extra buffer.
    """
    history = get_task_history()
    relevant_tasks = [
        t for t in history 
        if t.employee_id == employee_id and (task_type == "General" or t.task_type == task_type)
    ]
    
    if not relevant_tasks:
        # Default baseline if no past history exists
        return 1.0
        
    total_est = sum(t.estimated_hours for t in relevant_tasks)
    total_act = sum(t.actual_hours for t in relevant_tasks)
    
    if total_est == 0:
        return 1.0
        
    return round(total_act / total_est, 2)

def record_task_completion(record: TaskCompletionRecord) -> Optional[HistoricalTaskLog]:
    """
    Closes out a task, compares estimated vs actual duration, 
    and updates the learning feedback dataset.
    """
    tasks = get_all_tasks()
    task = next((t for t in tasks if t.task_id == record.task_id), None)
    
    if not task or not task.assigned_to:
        return None
        
    task.status = "Done"
    est_hours = task.estimated_effort_hours or record.actual_hours_spent
    variance = round(record.actual_hours_spent / est_hours, 2) if est_hours > 0 else 1.0
    
    # Infer simple category from skills
    task_type = "Backend" if "Python" in task.required_skills or "FastAPI" in task.required_skills else "General"
    
    log_entry = HistoricalTaskLog(
        task_id=task.task_id,
        employee_id=task.assigned_to,
        task_type=task_type,
        estimated_hours=est_hours,
        actual_hours=record.actual_hours_spent,
        variance_ratio=variance,
        completed_at=datetime.now()
    )
    
    get_task_history().append(log_entry)
    return log_entry