import instructor
from openai import OpenAI
from models import TaskExtraction

# Initialize client with local Ollama endpoint
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    ),
    mode=instructor.Mode.JSON,
)

def parse_manager_request(user_prompt: str) -> TaskExtraction:
    """
    Parses unstructured manager requests into a strictly validated TaskExtraction object.
    Provides explicit JSON schema anchors to prevent Llama 3 nesting hallucinations.
    """
    system_prompt = """
    You are an expert technical project manager.
    Extract the task details from the prompt and return top-level JSON fields matching TaskExtraction.

    CRITICAL RULES:
    1. Do NOT wrap the output in a root "task" key.
    2. "required_skills" MUST be a flat key-value mapping of skill name to an integer (1 to 5).
       Example: {"Python": 4, "Testing": 3}
       Do NOT use nested objects like {"Testing": {"required_level": 3}}.
    3. "priority" must be one of: "Low", "Medium", "High", "Critical".
    4. "estimated_effort_hours" must be a positive number.
    """

    parsed_task = client.chat.completions.create(
        model="llama3",
        response_model=TaskExtraction,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_retries=3
    )

    return parsed_task