from pydantic import BaseModel, Field
from enum import IntEnum, Enum
from typing import List, Dict, Optional

from datetime import datetime

class SkillLevel(IntEnum):
    BEGINNER = 1
    BASIC = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5

class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class TaskStatus(str, Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    REVIEW = "Review"
    DONE = "Done"

class Employee(BaseModel):
    employee_id: str
    name: str
    role: str
    skills: Dict[str, SkillLevel] = Field(description="Dictionary of skill names and their 1-5 proficiency level")
    working_hours_per_day: int = 8

class Task(BaseModel):
    task_id: str
    title: str
    description: str
    project: str
    priority: TaskPriority
    status: TaskStatus = TaskStatus.TODO
    required_skills: Dict[str, SkillLevel]
    estimated_effort_hours: Optional[float] = None
    dependencies: List[str] = Field(default_factory=list, description="List of Task IDs that must be completed first")
    assigned_to: Optional[str] = None

class CalendarEvent(BaseModel):
    event_id: str
    employee_id: str
    title: str
    start_time: datetime
    end_time: datetime
    is_private: bool = False

class WorkloadSummary(BaseModel):
    employee_id: str
    window_days: int
    total_base_hours: float
    meeting_hours: float
    active_task_hours: float
    remaining_capacity: float

class TaskExtraction(BaseModel):
    title: str = Field(description="A concise, professional title for the task")
    description: str = Field(description="A detailed description of what needs to be done")
    priority: TaskPriority
    required_skills: Dict[str, SkillLevel] = Field(description="Identify 1 to 3 necessary skills and assign a required 1-5 proficiency level.")
    estimated_effort_hours: float = Field(description="Estimate the hours required if not explicitly stated.")

class CandidateProfile(BaseModel):
    employee_id: str
    name: str
    role: str
    skill_match_score: float = Field(description="Percentage match of required skills (0.0 to 100.0)")
    capacity_hours: float = Field(description="Remaining capacity over the next 5 days")
    is_capacity_sufficient: bool = Field(description="True if capacity >= estimated effort")
    missing_skills: List[str] = Field(default_factory=list, description="Required skills the employee lacks")

class ConfidenceLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class AssignmentRecommendation(BaseModel):
    recommended_employee_id: str = Field(description="The ID of the recommended employee")
    confidence: ConfidenceLevel
    reasoning: str = Field(description="Clear explanation of WHY this employee was chosen, citing specific math and skills.")
    tradeoffs: str = Field(description="What are the risks? What about the other candidates?")

class ApprovalDecision(str, Enum):
    APPROVE = "Approve"
    REJECT = "Reject"
    MODIFY = "Modify"

class ManagerApprovalRequest(BaseModel):
    parsed_task: TaskExtraction
    recommended_employee_id: str
    decision: ApprovalDecision
    manager_feedback: Optional[str] = Field(default=None, description="Optional reason for rejection or modification")

# Add this below your existing models
class RequestType(str, Enum):
    TIME_OFF = "Time Off"
    TASK_DELAY = "Task Delay"
    REASSIGNMENT_REQUEST = "Reassignment Request"
    OTHER = "Other"

class ImpactReport(BaseModel):
    request_type: RequestType
    summary: str = Field(description="A brief summary of what the employee is asking for")
    affected_tasks: List[str] = Field(description="List of Task IDs that are directly impacted by this request")
    recommended_manager_action: str = Field(description="Actionable advice for the manager (e.g., 'Reassign T-123 to another developer' or 'Extend deadline by 2 days')")

class AuditLogEntry(BaseModel):
    log_id: str
    timestamp: datetime
    event_type: str  # e.g., "AI_RECOMMENDATION_GENERATED", "MANAGER_DECISION"
    task_title: str
    target_employee_id: Optional[str] = None
    ai_confidence: Optional[ConfidenceLevel] = None
    details: Dict[str, str] = Field(default_factory=dict)
    manager_decision: Optional[str] = None

class SubTaskPlan(BaseModel):
    title: str = Field(description="Subtask title")
    description: str = Field(description="Scope of this atomic unit")
    required_skills: Dict[str, SkillLevel]
    estimated_effort_hours: float
    dependencies: List[str] = Field(default_factory=list, description="Titles of prerequisites within this decomposition")

class TaskDecompositionResult(BaseModel):
    is_compound: bool = Field(description="True if the original request exceeds atomic granularity (>16 hours or multiple domains)")
    total_estimated_hours: float
    subtasks: List[SubTaskPlan] = Field(default_factory=list)
    suggested_timeline_days: float
    feasibility_notes: str = Field(description="Negotiation note if requested deadline is unrealistic")

class TaskCompletionRecord(BaseModel):
    task_id: str
    actual_hours_spent: float
    notes: Optional[str] = None

class HistoricalTaskLog(BaseModel):
    task_id: str
    employee_id: str
    task_type: str  # e.g., "Backend", "Frontend", "Testing"
    estimated_hours: float
    actual_hours: float
    variance_ratio: float  # actual / estimated
    completed_at: datetime

