import instructor
from openai import OpenAI
from models import TaskDecompositionResult

client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    ),
    mode=instructor.Mode.JSON,
)

def evaluate_and_decompose_task(manager_prompt: str, target_deadline_days: float = 3.0) -> TaskDecompositionResult:
    """
    Evaluates scope size. If compound, breaks it down into sequential subtasks 
    and checks if the requested deadline is realistic.
    """
    system_prompt = f"""
    You are an AI Delivery Manager specializing in Agile technical decomposition.
    Guidelines:
    1. If a task takes >16 hours or covers multiple separate engineering domains (e.g., UI + Backend + Testing), set is_compound=True.
    2. Decompose compound tasks into atomic subtasks of 2 to 8 hours each.
    3. Define strict prerequisite dependencies using the exact titles of preceding subtasks.
    4. Target deadline is {target_deadline_days} working days (8 hours/day capacity per engineer). 
       If total_estimated_hours exceeds realistic single-engineer parallelization within this timeframe,
       explicitly explain the delivery risk and propose an alternative deadline or split assignment in feasibility_notes.
    """

    user_prompt = f"MANAGER REQUEST: {manager_prompt}"

    result = client.chat.completions.create(
        model="llama3",
        response_model=TaskDecompositionResult,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_retries=3
    )

    return result