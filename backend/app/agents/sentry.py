from app.agents.state import AgentState
from app.agents.tools import post_to_platform, store_in_vault, save_draft_to_db
from app.config.database import SessionLocal
from app.models.content_draft import ContentDraft, ContentPlatform
from app.models.project_model import Project
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
# from langchain.agents.format_scratchpad import format_to_openai_functions
# from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
# from langchain.tools.render import format_tool_to_openai_function
# from langchain_community.tools.convert_to_openai import format_tool_to_openai_function
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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
    # Create Agent
    # Note: We trust the prompts to guide the agent to call tools.
    agent = create_agent(llm, tools=tools)

    # Prompt
    prompt_text = f"""
    You are Sentry, the Final Gatekeeper and Safety Officer.
    
    1. REVIEW the draft: '{draft}'
    2. DECIDE status:
       - 'approved': If excellent.
       - 'rejected': If unsafe.
       - 'pending': If unsure.
       
    3. EXECUTE:
       - If Approved AND 'best_time' is now: Call `post_to_platform` (args: content='{draft}', platform='Twitter', schedule_time='now'). Call `save_draft_to_db` (args: status='published', user_id={user_id}).
       - If Approved AND 'best_time' is future: Call `save_draft_to_db` (args: status='scheduled', scheduled_for='{best_time}', user_id={user_id}).
       - If Pending: Call `save_draft_to_db` (args: status='pending_approval', scheduled_for='{best_time}', user_id={user_id}).
       - If Rejected: Call `save_draft_to_db` (args: status='rejected', user_id={user_id}).
    
    4. RESPOND: Final Answer one word: 'published', 'scheduled', 'pending', or 'rejected'.
    """
    
    try:
        response = agent.invoke({"messages": [HumanMessage(content=prompt_text)]})
        
        # Parse output
        status = "pending"
        output_text = ""
        if isinstance(response, dict) and "messages" in response:
             output_text = response["messages"][-1].content
        elif isinstance(response, dict) and "output" in response:
             output_text = response["output"]
        else:
             output_text = str(response)
             
        # Infer status from output if tools didn't set it (Agent might just say "approved")
        lower_out = output_text.lower()
        if "published" in lower_out: status = "published"
        elif "scheduled" in lower_out: status = "scheduled"
        elif "rejected" in lower_out: status = "rejected"
        else: status = "pending"
        
        return {
            "sentry_approval_status": status,
            "chat_history": [HumanMessage(content=f"Sentry decision: {status}: {output_text}")]
        }
        
    except Exception as e:
        return {
            "sentry_approval_status": "error",
            "chat_history": [HumanMessage(content=f"Sentry error: {e}")]
        }
