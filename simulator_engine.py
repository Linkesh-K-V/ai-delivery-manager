from mock_data import get_employee_active_tasks, get_all_employees
from candidate_engine import rank_candidates
from models import TaskExtraction

def simulate_employee_absence(absent_employee_id: str) -> dict:
    """
    Simulates removing an employee from the workforce. Identifies their active tasks
    and calculates who should take them over and how it affects their capacity.
    """
    # 1. Identify the blast radius (which tasks are suddenly orphaned?)
    orphaned_tasks = get_employee_active_tasks(absent_employee_id)
    
    reassignment_plan = []
    
    for task in orphaned_tasks:
        # Translate our database Task into a TaskExtraction object for the engine
        task_req = TaskExtraction(
            title=task.title,
            description=task.description,
            priority=task.priority,
            required_skills=task.required_skills,
            estimated_effort_hours=task.estimated_effort_hours or 0.0
        )
        
        # 2. Run the deterministic engine, strictly excluding the absent employee
        candidates = rank_candidates(task_req, exclude_employee_ids=[absent_employee_id])
        
        if candidates:
            best_match = candidates[0]
            # 3. Calculate hypothetical capacity drop
            hypothetical_capacity = best_match.capacity_hours - task_req.estimated_effort_hours
            
            reassignment_plan.append({
                "task_id": task.task_id,
                "task_title": task.title,
                "recommended_replacement_id": best_match.employee_id,
                "replacement_name": best_match.name,
                "original_capacity": best_match.capacity_hours,
                "hypothetical_new_capacity": hypothetical_capacity
            })
        else:
            reassignment_plan.append({
                "task_id": task.task_id,
                "task_title": task.title,
                "error": "No viable candidates found in the remaining workforce."
            })

    return {
        "simulation_target": absent_employee_id,
        "tasks_affected": len(orphaned_tasks),
        "reassignment_plan": reassignment_plan
    }