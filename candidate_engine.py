from models import Employee, TaskExtraction, CandidateProfile
from mock_data import get_all_employees
from workload_engine import calculate_employee_capacity
from learning_engine import get_employee_calibration_factor

def score_employee_skills(employee: Employee, required_skills: dict) -> tuple[float, list[str]]:
    if not required_skills:
        return 100.0, []

    total_possible_score = sum(required_skills.values())
    actual_score = 0
    missing = []

    for req_skill, req_level in required_skills.items():
        emp_level = employee.skills.get(req_skill)
        if emp_level:
            actual_score += min(emp_level, req_level)
            if emp_level < req_level:
                missing.append(f"{req_skill} (Needs {req_level.name}, has {emp_level.name})")
        else:
            missing.append(f"{req_skill} (Missing entirely)")

    match_percentage = (actual_score / total_possible_score) * 100
    return round(match_percentage, 1), missing

def rank_candidates(task_req: TaskExtraction, exclude_employee_ids: list[str] = None) -> list[CandidateProfile]:
    if exclude_employee_ids is None:
        exclude_employee_ids = []
        
    all_employees = get_all_employees()
    employees = [e for e in all_employees if e.employee_id not in exclude_employee_ids]
    candidates = []
    
    effort = task_req.estimated_effort_hours or 0.0

    for emp in employees:
        # 1. Calculate Skill Match
        score, missing = score_employee_skills(emp, task_req.required_skills)
        
        # 2. Fetch Deterministic Workload
        workload = calculate_employee_capacity(emp, days=5)
        
        # 3. Apply Statistical Learning Calibration Factor
        calibration_factor = get_employee_calibration_factor(emp.employee_id, task_type="Backend")
        adjusted_effort = effort * calibration_factor
        
        # 4. Assess Capacity using calibrated effort
        is_sufficient = workload.remaining_capacity >= adjusted_effort
        
        profile = CandidateProfile(
            employee_id=emp.employee_id,
            name=emp.name,
            role=emp.role,
            skill_match_score=score,
            capacity_hours=workload.remaining_capacity,
            is_capacity_sufficient=is_sufficient,
            missing_skills=missing
        )
        candidates.append(profile)

    candidates.sort(key=lambda x: (x.skill_match_score, x.capacity_hours), reverse=True)
    return candidates