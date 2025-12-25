from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.scout import scout_node
from app.agents.scripter import scripter_node
from app.agents.critic import critic_node
from app.agents.analyst import analyst_node
from app.agents.sentry import sentry_node
from app.agents.engineer import engineer_node
from app.agents.guru import guru_node

def should_continue(state: AgentState):
    if state["is_good_enough"]:
        return "analyst"
    if state["revision_count"] > 3: 
        return "end"
    return "revise"

def sentry_router(state: AgentState):
    status = state.get("sentry_approval_status", "pending")
    if status == "approved" or status == "published":
        return "engineer"
    elif status == "rejected":
        return "scripter"
    else: # pending / pending_user_review
        return "end" # Wait for user input

def start_router(state: AgentState):
    """
    Routes to either the Creation Pipeline (Scout) or the Chatbot (Guru).
    """
    user_input = state.get("input", "").lower()
    chat_keywords = ["how", "what", "show", "help", "who", "query", "question", "monitor", "brand", "stats"]
    
    # If explicit creation keywords are missing and it looks like a question, go to Guru
    if any(k in user_input for k in chat_keywords) and not "create" in user_input and not "write" in user_input:
        return "guru"
    
    return "scout"

# Initialize Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("scout", scout_node)
workflow.add_node("scripter", scripter_node)
workflow.add_node("critic", critic_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("sentry", sentry_node)
workflow.add_node("engineer", engineer_node)
workflow.add_node("guru", guru_node)

# Add Edges
# Start Router replaces simple entry point
workflow.set_conditional_entry_point(
    start_router,
    {
        "scout": "scout",
        "guru": "guru"
    }
)

workflow.add_edge("scout", "scripter")
workflow.add_edge("scripter", "critic")

# Conditional Edge from Critic
workflow.add_conditional_edges(
    "critic",
    should_continue,
    {
        "revise": "scripter",
        "analyst": "analyst",
        "end": END
    }
)

# Connect Analyst to Sentry
workflow.add_edge("analyst", "sentry")

# Conditional Edge from Sentry (HITL)
workflow.add_conditional_edges(
    "sentry",
    sentry_router,
    {
        "engineer": "engineer",
        "scripter": "scripter",
        "end": END
    }
)

workflow.add_edge("engineer", END)
workflow.add_edge("guru", END)

from langgraph.checkpoint.memory import MemorySaver

# ... (Previous code)

# Compile with Checkpointer for persistence (required for HITL)
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
