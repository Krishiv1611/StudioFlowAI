from app.agents.state import AgentState
from app.agents.tools import post_to_platform, store_in_vault, save_draft_to_db
from app.config.database import SessionLocal
from app.models.content_draft import ContentDraft, ContentPlatform
from app.models.project_model import Project
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent, AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.tools.render import format_tool_to_openai_function
from langchain_community.tools.convert_to_openai import format_tool_to_openai_function
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings
import os

# Helper to get model
def get_model(provider: str):
    return ChatGoogleGenerativeAI(
        model="gemini-3.0-flash",
        temperature=0.1,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

def sentry_node(state: AgentState):
    """
    Sentry Agent: The Gatekeeper (Now with a Brain).
    Responsible for final approval, safety checks, and database management.
    """
    llm = get_model(state.get("model_provider", "gemini"))
    
    # Define Tools
    tools = [post_to_platform, store_in_vault, save_draft_to_db]
    llm_with_tools = llm.bind_tools(tools)
    
    # Current Context
    draft = state.get("draft", "")
    best_time = state.get("best_time", "now")
    user_id = state.get("user_id", 1)
    approval_status = state.get("sentry_approval_status", "pending")
    
    # If already approved/rejected by Human (via API), we skip the brain and just execute
    if approval_status in ["approved", "published", "rejected"]:
        # Logic to handle API-triggered resumption
        if approval_status == "approved":
             # Post & Store
             save_draft_to_db.invoke({"user_id": user_id, "content": draft, "status": "published", "platform": "Twitter"})
             res = post_to_platform.invoke({"content": draft, "platform": "Twitter", "schedule_time": best_time})
             store_in_vault.invoke({"content": f"PUBLISHED: {draft}", "user_id": user_id})
             return {"sentry_approval_status": "published", "chat_history": [HumanMessage(content=f"Published: {res}")]}
        return {} # Pass through if rejected

    # Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are Sentry, the Final Gatekeeper and Safety Officer.
        
        1. REVIEW the draft: '{draft}'
        2. DECIDE status:
           - 'approved': If excellent.
           - 'rejected': If unsafe.
           - 'pending': If unsure.
           
        3. EXECUTE:
           - If Approved AND 'best_time' is now: Call `post_to_platform`. Save to DB as 'published'.
           - If Approved AND 'best_time' is future: Pass `scheduled_for={best_time}` to `save_draft_to_db` with status='scheduled'.
           - If Pending: Call `save_draft_to_db` with status='pending_approval' and `scheduled_for={best_time}` (so user sees proposed time).
           - If Rejected: Save with status='rejected'.
        
        4. RESPOND: Final Answer one word: 'published', 'scheduled', 'pending', or 'rejected'.
        """),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # ...
    
    response = llm_with_tools.invoke(prompt.format(draft=draft, best_time=best_time, agent_scratchpad=[]))
    # ... (Rest of logic needs minimal update as the prompt drives the tool usage)
    # But we need to update the manual tool execution loop to ensure args are passed.
    
    status = "pending" # Default
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            t_name = tool_call['name']
            t_args = tool_call['args']
            
            # Auto-inject keys if missed by LLM
            if t_name == "save_draft_to_db":
                if "user_id" not in t_args: t_args["user_id"] = user_id
                if "content" not in t_args: t_args["content"] = draft
                # If LLM didn't pass scheduled_for, inject best_time if pending
                if t_args.get("status") in ["pending_approval", "scheduled"] and "scheduled_for" not in t_args:
                     t_args["scheduled_for"] = str(best_time)
                     
                save_draft_to_db.invoke(t_args)
                status = t_args.get('status', 'pending')
                    
            elif t_name == "post_to_platform":
                post_to_platform.invoke(t_args)
                status = "published"
                
            elif t_name == "store_in_vault":
                store_in_vault.invoke(t_args)

    # Fallback
    if not hasattr(response, 'tool_calls') or not response.tool_calls:
         save_draft_to_db.invoke({
             "user_id": user_id, 
             "content": draft, 
             "status": "pending_approval", 
             "platform": "Twitter",
             "scheduled_for": str(best_time)
         })
         status = "pending"

    return {
        "sentry_approval_status": status,
        "chat_history": [HumanMessage(content=f"Sentry decision: {status}")]
    }
