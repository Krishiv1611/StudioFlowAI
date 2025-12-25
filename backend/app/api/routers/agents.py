from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.api.deps import get_current_user
from app.models.user_model import User
from app.agents.graph import app as agent_app
from app.agents.state import AgentState
from langchain_core.messages import HumanMessage
import uuid
import asyncio

router = APIRouter(prefix="/agent", tags=["Agent Workflow"])

# In-memory store for background task results (Product should use DB/Redis)
params_store = {} 

class AgentRequest:
    input: str
    model_provider: str = "gemini"

@router.post("/run")
async def run_agent(
    request: dict, 
    current_user: User = Depends(get_current_user)
):
    """
    Start a new agent workflow (Drafting or Chat).
    Returns a thread_id to track progress.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "input": request.get("input", ""),
        "user_id": current_user.id,
        "model_provider": request.get("model_provider", "gemini"),
        "chat_history": [],
        "revision_count": 0,
        "is_good_enough": False,
        "sentry_approval_status": "pending"
    }
    
    # We kick off the run. 
    # Since we want to return immediately, we can stream the first chunk or just return thread_id.
    # For HITL, we need to execute until it pauses.
    
    # Run slightly asynchronously to let it reach Sentry or End
    # In a real queue system (Celery), this would be offloaded.
    # Here we await the first step to initialize.
    
    async for event in agent_app.astream(initial_state, config=config):
        pass # Process until pause or end
        
    # Get current state after run
    snapshot = agent_app.get_state(config)
    
    return {
        "thread_id": thread_id, 
        "next_step": snapshot.next,
        "values": snapshot.values if snapshot.values else None
    }

@router.get("/status/{thread_id}")
async def get_status(thread_id: str, current_user: User = Depends(get_current_user)):
    """
    Get the current state of a workflow.
    """
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = agent_app.get_state(config)
    
    if not snapshot.values:
        return {"status": "completed_or_invalid", "values": None}
        
    return {
        "next_step": snapshot.next,
        "values": {
            "draft": snapshot.values.get("draft"),
            "analyst_report": snapshot.values.get("analyst_report"),
            "sentry_status": snapshot.values.get("sentry_approval_status"),
            "chat_history": [m.content for m in snapshot.values.get("chat_history", []) if isinstance(m, HumanMessage)]
        }
    }

@router.post("/approve/{thread_id}")
async def approve_draft(
    thread_id: str, 
    approval: dict, # {"action": "approve" or "reject"}
    current_user: User = Depends(get_current_user)
):
    """
    Approve or Reject a draft at the Sentry gate.
    """
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = agent_app.get_state(config)
    
    if not snapshot.values:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    action = approval.get("action", "reject")
    status_update = "approved" if action == "approve" else "rejected"
    
    # Update state via new command
    agent_app.update_state(config, {"sentry_approval_status": status_update})
    
    # Resume execution
    async for event in agent_app.astream(None, config=config):
        pass
        
    # Get final result
    snapshot = agent_app.get_state(config)
    return {
        "status": "resumed", 
        "values": snapshot.values
    }

@router.post("/chat")
async def chat_with_guru(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Direct endpoint for 'Guru' chat.
    Conceptually similar to 'run' but optimized for synchronous response.
    """
    # Reuse run logic but return the last message
    thread_id = str(uuid.uuid4()) # New chat session every time for now (or pass thread_id)
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "input": request.get("input", ""),
        "user_id": current_user.id,
        "model_provider": request.get("model_provider", "gemini"),
        "chat_history": []
    }
    
    response_text = ""
    async for event in agent_app.astream(initial_state, config=config):
        # In Guru flow, we want the final output
        for k, v in event.items():
            if "chat_history" in v:
                response_text = v['chat_history'][-1].content
                
    return {"response": response_text, "thread_id": thread_id}
