from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from mock_data import get_all_employees, get_all_tasks, execute_task_assignment
from models import Employee, Task, WorkloadSummary, TaskExtraction, CandidateProfile, ManagerApprovalRequest, ApprovalDecision, ImpactReport
from workload_engine import calculate_employee_capacity
from llm_parser import parse_manager_request
from candidate_engine import rank_candidates
from llm_reasoner import generate_recommendation
from employee_agent import analyze_employee_impact
from simulator_engine import simulate_employee_absence
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from models import AuditLogEntry
from audit_service import record_audit_event, get_audit_logs
from typing import List, Dict, Optional
from datetime import datetime
from models import TaskDecompositionResult
from decomposition_engine import evaluate_and_decompose_task
from agent_graph import orchestrator_app
from models import TaskCompletionRecord, HistoricalTaskLog
from learning_engine import record_task_completion, get_employee_calibration_factor
from mock_data import get_task_history

app = FastAPI(
    title="AI Delivery Manager API",
    description="Backend for the Intelligent Workforce Management System",
    version="0.1.0"
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Delivery Manager API is running"}

@app.get("/api/employees", response_model=List[Employee])
def list_employees():
    """Retrieve all employees in the organization."""
    return get_all_employees()

@app.get("/api/tasks", response_model=List[Task])
def list_tasks():
    """Retrieve all tasks in the system."""
    return get_all_tasks()

@app.get("/api/employees/{employee_id}/workload", response_model=WorkloadSummary)
def get_employee_workload(employee_id: str, days: int = 5):
    """Calculate the remaining capacity for a specific employee."""
    employees = get_all_employees()
    employee = next((e for e in employees if e.employee_id == employee_id), None)
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    return calculate_employee_capacity(employee, days)

class DecomposeRequest(BaseModel):
    prompt: str
    target_deadline_days: Optional[float] = 3.0

@app.post("/api/tasks/decompose", response_model=TaskDecompositionResult)
def decompose_large_task(request: DecomposeRequest):
    """
    Analyzes whether a request is a compound task, decomposes it into 
    subtasks with dependencies, and evaluates deadline feasibility.
    """
    try:
        plan = evaluate_and_decompose_task(
            manager_prompt=request.prompt,
            target_deadline_days=request.target_deadline_days or 3.0
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decomposition failed: {str(e)}")

class TaskRequest(BaseModel):
    prompt: str

@app.post("/api/tasks/analyze", response_model=TaskExtraction)
def analyze_task_request(request: TaskRequest):
    """Converts a natural language prompt into a structured task definition."""
    try:
        parsed_task = parse_manager_request(request.prompt)
        return parsed_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Parsing failed: {str(e)}")

@app.post("/api/candidates/rank", response_model=List[CandidateProfile])
def get_ranked_candidates(task: TaskExtraction):
    """
    Takes a structured task definition and returns a deterministically 
    ranked list of employee candidates based on skills and workload.
    """
    try:
        candidates = rank_candidates(task)
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")

class EndToEndRequest(BaseModel):
    manager_prompt: str

@app.post("/api/workflow/recommend", response_model=dict)
def full_recommendation_workflow(request: EndToEndRequest):
    """
    The full AI Delivery Manager workflow:
    1. AI parses natural language -> 2. Math Engine ranks candidates -> 3. AI reasons and recommends.
    """
    try:
        # Step 1: LLM extracts task details from text
        task_req = parse_manager_request(request.manager_prompt)
        
        # Step 2: Deterministic Engine evaluates all employees and sorts them
        all_candidates = rank_candidates(task_req)
        
        # Keep only the top 3 to avoid overwhelming the LLM context window
        top_3_candidates = all_candidates[:3]
        
        # Step 3: LLM analyzes the facts and writes the business case
        final_recommendation = generate_recommendation(task_req, top_3_candidates)

        # Step 4: Record audit log for recommendation generation
        record_audit_event(
            event_type="AI_RECOMMENDATION_GENERATED",
            task_title=task_req.title,
            target_employee_id=final_recommendation.recommended_employee_id,
            ai_confidence=final_recommendation.confidence,
            details={
                "reasoning_summary": final_recommendation.reasoning[:120] + "...",
                "candidate_pool_size": str(len(top_3_candidates))
            }
        )
        
        # Return the complete state to the frontend
        return {
            "parsed_task": task_req,
            "top_candidates": top_3_candidates,
            "ai_recommendation": final_recommendation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")

@app.post("/api/workflow/approve")
def process_manager_approval(approval: ManagerApprovalRequest):
    """
    The final Human-in-the-Loop step. Executes the assignment only if approved.
    """
    # Record manager decision in audit trail
    record_audit_event(
        event_type="MANAGER_DECISION",
        task_title=approval.parsed_task.title,
        target_employee_id=approval.recommended_employee_id,
        manager_decision=approval.decision.value,
        details={"feedback": approval.manager_feedback or "None"}
    )
    
    if approval.decision == ApprovalDecision.APPROVE:
        # The manager approved! Execute the database transaction.
        new_task = execute_task_assignment(
            task_req=approval.parsed_task, 
            assigned_employee_id=approval.recommended_employee_id
        )
        return {
            "status": "Success",
            "message": f"Task officially assigned to {approval.recommended_employee_id}",
            "task": new_task
        }
        
    elif approval.decision == ApprovalDecision.REJECT:
        # The manager rejected it. Do nothing but log it.
        return {
            "status": "Rejected",
            "message": "Recommendation rejected by manager. Task was not created.",
            "feedback_logged": approval.manager_feedback
        }

class EmployeeMessageRequest(BaseModel):
    employee_id: str
    message: str

@app.post("/api/employee/request", response_model=ImpactReport)
def process_employee_message(request: EmployeeMessageRequest):
    """
    Processes an employee's natural language request, determines the impact 
    on their workload, and prepares a report for the manager.
    """
    try:
        report = analyze_employee_impact(request.employee_id, request.message)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impact Analysis failed: {str(e)}")

@app.get("/api/simulate/absence/{employee_id}")
def run_absence_simulation(employee_id: str):
    """
    Runs a Level 1 Bounded Simulation: What happens to active tasks if this employee disappears?
    Does NOT mutate the database.
    """
    try:
        report = simulate_employee_absence(employee_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/dashboard")
def get_dashboard():
    return FileResponse("static/index.html")

@app.get("/api/audit/logs", response_model=List[AuditLogEntry])
def read_audit_logs():
    """Retrieve immutable audit trail for compliance and explainability auditing."""
    return get_audit_logs()

@app.post("/api/workflow/recommend", response_model=dict)
def full_recommendation_workflow(request: EndToEndRequest):
    """
    Executes the task allocation pipeline via a compiled LangGraph state machine.
    """
    initial_state = {
        "manager_prompt": request.manager_prompt,
        "parsed_task": None,
        "top_candidates": [],
        "ai_recommendation": None,
        "error": None
    }
    
    # Run the state graph synchronously
    final_state = orchestrator_app.invoke(initial_state)
    
    if final_state.get("error"):
        raise HTTPException(status_code=500, detail=final_state["error"])
        
    task_req = final_state["parsed_task"]
    rec = final_state["ai_recommendation"]
    candidates = final_state["top_candidates"]
    
    # Keep our audit ledger intact
    record_audit_event(
        event_type="AI_RECOMMENDATION_GENERATED",
        task_title=task_req.title,
        target_employee_id=rec.recommended_employee_id,
        ai_confidence=rec.confidence,
        details={
            "orchestrator": "LangGraph_v0.1",
            "reasoning_summary": rec.reasoning[:120] + "...",
            "candidate_pool_size": str(len(candidates))
        }
    )
    
    return {
        "parsed_task": task_req,
        "top_candidates": candidates,
        "ai_recommendation": rec
    }

@app.post("/api/tasks/complete", response_model=dict)
def complete_task(record: TaskCompletionRecord):
    """
    Marks a task as completed, logs actual effort vs estimated effort, 
    and refines the learning loop.
    """
    log_entry = record_task_completion(record)
    if not log_entry:
        raise HTTPException(status_code=404, detail="Task not found or not assigned")
        
    return {
        "status": "Task marked Done",
        "historical_log": log_entry,
        "new_calibration_factor": get_employee_calibration_factor(log_entry.employee_id)
    }

@app.get("/api/analytics/historical", response_model=List[HistoricalTaskLog])
def list_history():
    """Retrieve full historical logs for audit and performance tracking."""
    return get_task_history()

@app.get("/api/dashboard/overview")
def get_dashboard_overview():
    """Returns organizational capacity, active tasks, and latest audit logs."""
    employees = get_all_employees()
    overview = []
    
    for emp in employees:
        workload = calculate_employee_capacity(emp, days=5)
        tasks = get_employee_active_tasks(emp.employee_id)
        overview.append({
            "employee_id": emp.employee_id,
            "name": emp.name,
            "role": emp.role,
            "skills": emp.skills,
            "remaining_capacity": workload.remaining_capacity,
            "meeting_hours": workload.meeting_hours,
            "active_tasks_count": len(tasks)
        })
        
    return {
        "team_workload": overview,
        "recent_audits": get_audit_logs()[:5],
        "active_task_count": len([t for t in get_all_tasks() if t.status != "Done"])
    }