from typing import TypedDict, Annotated, List, Dict, Any
import operator

class AgentState(TypedDict):
    input: str
    user_id: int
    model_provider: str # Options: "groq", "gemini"
    chat_history: List[Any]
    
    # Content Generation Flow
    trend_data: str
    draft: str
    critique: str
    virality_score: float
    
    # RAG/Memory
    research_context: List[str]
    
    # Control Flags
    revision_count: int
    is_good_enough: bool
    
    # New Analyst/Engineer Logic
    follower_count: int # For Reach
    best_time: str
    predicted_reach: float
    analyst_report: str
    engineer_report: str
    
    # Sentry / HITL
    sentry_approval_status: str # "pending", "approved", "rejected", "published"
