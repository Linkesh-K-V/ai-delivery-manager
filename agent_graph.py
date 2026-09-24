from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from models import TaskExtraction, CandidateProfile, AssignmentRecommendation
from llm_parser import parse_manager_request
from candidate_engine import rank_candidates
from llm_reasoner import generate_recommendation

# 1. Define the Graph State Schema
class DeliveryManagerState(TypedDict):
    manager_prompt: str
    parsed_task: Optional[TaskExtraction]
    top_candidates: List[CandidateProfile]
    ai_recommendation: Optional[AssignmentRecommendation]
    error: Optional[str]

# 2. Define Individual Graph Nodes
def parse_task_node(state: DeliveryManagerState) -> dict:
    """Agent Node 1: Converts unstructured prompt to Pydantic TaskExtraction."""
    try:
        task = parse_manager_request(state["manager_prompt"])
        return {"parsed_task": task}
    except Exception as e:
        return {"error": f"Task parsing failed: {str(e)}"}

def rank_candidates_node(state: DeliveryManagerState) -> dict:
    """Deterministic Node 2: Evaluates skills & calendar capacity."""
    if state.get("error"):
        return {}
    try:
        task = state["parsed_task"]
        candidates = rank_candidates(task)
        # Pass the top 3 candidates to the reasoner
        return {"top_candidates": candidates[:3]}
    except Exception as e:
        return {"error": f"Candidate ranking failed: {str(e)}"}

def reason_recommendation_node(state: DeliveryManagerState) -> dict:
    """Agent Node 3: Synthesizes facts into human-readable trade-off reasoning."""
    if state.get("error"):
        return {}
    try:
        recommendation = generate_recommendation(
            task=state["parsed_task"],
            top_candidates=state["top_candidates"]
        )
        return {"ai_recommendation": recommendation}
    except Exception as e:
        return {"error": f"Reasoning generation failed: {str(e)}"}

# 3. Assemble and Compile the Graph
workflow = StateGraph(DeliveryManagerState)

workflow.add_node("parser", parse_task_node)
workflow.add_node("ranker", rank_candidates_node)
workflow.add_node("reasoner", reason_recommendation_node)

# Set execution flow: START -> parser -> ranker -> reasoner -> END
workflow.set_entry_point("parser")
workflow.add_edge("parser", "ranker")
workflow.add_edge("ranker", "reasoner")
workflow.add_edge("reasoner", END)

orchestrator_app = workflow.compile()