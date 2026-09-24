import instructor
from openai import OpenAI
from models import ImpactReport
from mock_data import get_employee_active_tasks

# Initialize our local Llama 3 client via Instructor
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    ),
    mode=instructor.Mode.JSON,
)

def analyze_employee_impact(employee_id: str, employee_message: str) -> ImpactReport:
    """
    Reads an employee's natural language request, cross-references it with 
    their active tasks, and generates an impact report for the manager.
    """
    # 1. Fetch the exact factual data for this specific employee
    active_tasks = get_employee_active_tasks(employee_id)
    
    # 2. Convert to JSON string for the prompt
    tasks_json = [t.model_dump() for t in active_tasks]
    
    system_prompt = """
    You are an AI Workforce Assistant. An employee has sent a message regarding their schedule or tasks.
    Your job is to analyze their message, cross-reference it with their currently assigned tasks, 
    identify exactly which tasks are at risk, and recommend a mitigation strategy for the manager.
    Do not invent task IDs. Only use the tasks provided in the JSON data.
    """

    user_prompt = f"""
    EMPLOYEE MESSAGE: "{employee_message}"
    
    CURRENT ACTIVE TASKS FOR EMPLOYEE: 
    {tasks_json}
    
    Analyze the impact and generate the report.
    """

    # 3. Call Llama 3 to structure the impact
    report = client.chat.completions.create(
        model="llama3",
        response_model=ImpactReport,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_retries=3
    )
    
    return report