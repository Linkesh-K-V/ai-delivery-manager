import instructor
from openai import OpenAI
from models import TaskExtraction, CandidateProfile, AssignmentRecommendation

# Initialize our local Llama 3 client via Instructor
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    ),
    mode=instructor.Mode.JSON,
)

def generate_recommendation(task: TaskExtraction, top_candidates: list[CandidateProfile]) -> AssignmentRecommendation:
    """
    Takes the structured task and deterministic candidate list, and uses the LLM 
    to generate a nuanced, human-readable recommendation and trade-off analysis.
    """
    
    # Convert Pydantic models to JSON strings so the LLM can read them
    task_json = task.model_dump_json(indent=2)
    candidates_json = [c.model_dump() for c in top_candidates]
    
    system_prompt = """
    You are an AI Workforce Allocation Expert. 
    You are provided with a new Task and a list of Candidate Employees pre-ranked by an algorithm.
    Your job is to recommend the best candidate, state your confidence, and explain your reasoning.
    
    RULES:
    1. Base your reasoning ONLY on the data provided. Do not invent skills or capacity.
    2. If the top candidate's capacity is lower than the task effort, you MUST drop your confidence to MEDIUM or LOW and explain the risk.
    3. Explain the tradeoffs (e.g., "Candidate 2 has the skills but lacks the capacity").
    """

    user_prompt = f"""
    TASK DETAILS:
    {task_json}
    
    TOP CANDIDATES:
    {candidates_json}
    
    Please provide your final recommendation.
    """

    # Call Llama 3 to generate the structured recommendation
    recommendation = client.chat.completions.create(
        model="llama3",
        response_model=AssignmentRecommendation,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_retries=3
    )
    
    return recommendation